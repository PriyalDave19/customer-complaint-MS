import os
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from agent.state import AgentState
import schemas
from dotenv import load_dotenv

load_dotenv()

# We will use llama-3.3-70b-versatile for complex reasoning/extraction
# gemma2-9b-it could also be used but 70b is better for JSON structured output
# The assignment mentions "gemma2-9b-it model ... You may also consider llama-3.3-70b-versatile"
MODEL_NAME = "llama-3.3-70b-versatile"

def extract_information(state: AgentState):
    """
    Extract structured information from the raw complaint text.
    """
    complaint_text = state["complaint_text"]
    
    llm = ChatGroq(model=MODEL_NAME, temperature=0)
    structured_llm = llm.with_structured_output(schemas.ComplaintBase)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert pharmaceutical Quality Assurance assistant. "
                   "Your task is to extract customer complaint details from the provided text into a structured format. "
                   "If a field is not present in the text, leave it as null/None. "
                   "For dates, try to format them nicely (e.g., YYYY-MM-DD or DD-MMM-YYYY)."),
        ("human", "Extract info from this complaint:\n\n{text}")
    ])
    
    chain = prompt | structured_llm
    
    try:
        extracted_data = chain.invoke({"text": complaint_text})
        return {"extracted_data": extracted_data}
    except Exception as e:
        return {"errors": f"Extraction failed: {str(e)}"}

def assess_risk(state: AgentState):
    """
    Assess risk and recommend CAPA based on extracted information.
    """
    extracted = state.get("extracted_data")
    if not extracted or state.get("errors"):
        return state
        
    llm = ChatGroq(model=MODEL_NAME, temperature=0.2)
    structured_llm = llm.with_structured_output(schemas.RiskAssessmentBase)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a pharmaceutical Quality Management System (QMS) expert. "
                   "Based on the following extracted complaint details, provide a risk assessment. "
                   "1. Determine the risk_class (e.g., Critical, Major, Minor). "
                   "2. Provide a brief root_cause_hypothesis. "
                   "3. Suggest a capa_recommendation (Corrective and Preventive Action)."),
        ("human", "Complaint Details:\n"
                  "Issue: {description}\n"
                  "Product: {product}\n"
                  "Severity noted: {severity}\n\n"
                  "Please provide the risk assessment.")
    ])
    
    chain = prompt | structured_llm
    
    try:
        risk_analysis = chain.invoke({
            "description": extracted.description or "No description provided",
            "product": extracted.product_name or "Unknown",
            "severity": extracted.severity or "Unknown"
        })
        return {"risk_analysis": risk_analysis}
    except Exception as e:
        return {"errors": f"Risk assessment failed: {str(e)}"}

# Build Graph
builder = StateGraph(AgentState)
builder.add_node("extract_information", extract_information)
builder.add_node("assess_risk", assess_risk)

builder.set_entry_point("extract_information")
builder.add_edge("extract_information", "assess_risk")
builder.add_edge("assess_risk", END)

agent_graph = builder.compile()

async def run_agent(text: str) -> dict:
    """Helper to run the graph and format response."""
    # Ensure API key is set
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        # Return mock data if no key is provided, so the UI can still be tested
        return {
            "extracted_data": schemas.ComplaintBase(
                source="Email",
                customer_name="John Doe",
                product_name="Paracetamol 500mg",
                batch_number="B12345",
                quantity_affected=100,
                description="Mock Data: Please configure GROQ_API_KEY in backend/.env. The pills are broken.",
                severity="High",
                priority="High"
            ),
            "risk_analysis": schemas.RiskAssessmentBase(
                risk_class="Major",
                root_cause_hypothesis="Manufacturing defect during tableting.",
                capa_recommendation="Review tableting machine settings for batch B12345."
            )
        }

    initial_state = {"complaint_text": text, "extracted_data": None, "risk_analysis": None, "errors": None}
    
    result = await agent_graph.ainvoke(initial_state)
    
    if result.get("errors"):
        raise Exception(result["errors"])
        
    return {
        "extracted_data": result["extracted_data"],
        "risk_analysis": result["risk_analysis"]
    }
