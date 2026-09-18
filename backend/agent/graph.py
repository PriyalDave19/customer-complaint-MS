import os
import re
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from agent.state import AgentState
import schemas
from dotenv import load_dotenv

load_dotenv()

# Groq has decommissioned the Llama/Gemma ids this project originally used
# (llama-3.3-70b-versatile, gemma2-9b-it): they now return a model_not_found error.
# The models available on this account are:
#   openai/gpt-oss-120b, openai/gpt-oss-20b, openai/gpt-oss-safeguard-20b,
#   groq/compound, groq/compound-mini, qwen/qwen3.8-27b, allam-2-7b, whisper-*
# gpt-oss-120b is the strongest of those and supports Groq's strict structured
# outputs (see structured_llm below). Override via GROQ_MODEL in backend/.env.
MODEL_NAME = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

def structured_llm(schema, temperature: float = 0):
    """
    ChatGroq bound to a schema. Uses Groq's json_schema structured outputs
    (constrained decoding when strict is supported) instead of the default
    function-calling method: gpt-oss models sometimes write the JSON directly
    rather than calling the tool, which surfaces as "tool_use_failed".
    """
    llm = ChatGroq(model=MODEL_NAME, temperature=temperature)
    return llm.with_structured_output(schema, method="json_schema", strict=True)

_SEVERITY_SYNONYMS = {
    "critical": "Critical", "severe": "Critical", "high": "Critical", "very high": "Critical",
    "major": "Major", "moderate": "Major", "medium": "Major", "significant": "Major",
    "minor": "Minor", "low": "Minor", "trivial": "Minor", "cosmetic": "Minor",
}
_PRIORITY_SYNONYMS = {
    "high": "High", "urgent": "High", "critical": "High", "immediate": "High",
    "medium": "Medium", "moderate": "Medium", "normal": "Medium", "standard": "Medium",
    "low": "Low", "minor": "Low", "routine": "Low",
}
_DATE_FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
                 "%d-%b-%Y", "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y", "%Y-%m-%dT%H:%M:%S")

def _pick_option(value, options, synonyms):
    """Map a free-text AI value onto one of the form's fixed <select> options."""
    if not value:
        return None
    key = str(value).strip().lower()
    for opt in options:
        if key == opt.lower():
            return opt
    return synonyms.get(key)

def _iso_date(value):
    """Coerce assorted date spellings to YYYY-MM-DD so <input type=date> shows them."""
    if not value:
        return None
    text = str(value).strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    m = re.search(r"\d{4}-\d{2}-\d{2}", text)
    return m.group(0) if m else text

def normalize_extracted(data: schemas.ComplaintBase) -> schemas.ComplaintBase:
    """Align extracted values with what the frontend form controls accept."""
    return data.model_copy(update={
        "severity": _pick_option(data.severity, schemas.SEVERITY_OPTIONS, _SEVERITY_SYNONYMS),
        "priority": _pick_option(data.priority, schemas.PRIORITY_OPTIONS, _PRIORITY_SYNONYMS),
        "manufacturing_date": _iso_date(data.manufacturing_date),
        "expiry_date": _iso_date(data.expiry_date),
        "complaint_date": _iso_date(data.complaint_date),
    })

def extract_information(state: AgentState):
    """
    Extract structured information from the raw complaint text.
    """
    complaint_text = state["complaint_text"]
    
    extractor = structured_llm(schemas.ComplaintBase)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert pharmaceutical Quality Assurance assistant. "
                   "Your task is to extract customer complaint details from the provided text into a structured format. "
                   "If a field is not present in the text, leave it as null/None. "
                   "Always format dates as YYYY-MM-DD. "
                   "severity must be one of Critical, Major, Minor and priority one of High, Medium, Low; "
                   "infer them from the tone and impact described if not stated explicitly."),
        ("human", "Extract info from this complaint:\n\n{text}")
    ])
    
    chain = prompt | extractor
    
    try:
        extracted_data = chain.invoke({"text": complaint_text})
        return {"extracted_data": normalize_extracted(extracted_data)}
    except Exception as e:
        return {"errors": f"Extraction failed: {str(e)}"}

def assess_risk(state: AgentState):
    """
    Assess risk and recommend CAPA based on extracted information.
    """
    extracted = state.get("extracted_data")
    if not extracted or state.get("errors"):
        return state
        
    assessor = structured_llm(schemas.RiskAssessmentBase, temperature=0.2)
    
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
    
    chain = prompt | assessor
    
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
                product_name="Paracetamol",
                product_strength="500mg",
                batch_number="B12345",
                manufacturing_date="2023-01-15",
                expiry_date="2025-01-14",
                quantity_affected=100,
                complaint_type="Packaging Defect",
                complaint_date="2023-10-25",
                description="Mock Data: Please configure GROQ_API_KEY in backend/.env. The pills are broken.",
                severity="Critical",
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
        "risk_analysis": result.get("risk_analysis") or _risk_unavailable()
    }

def _risk_unavailable() -> schemas.RiskAssessmentBase:
    # ExtractionResponse.risk_analysis is required, so never return None here.
    return schemas.RiskAssessmentBase(
        risk_class="Not assessed",
        root_cause_hypothesis="Risk assessment was not produced for this complaint.",
        capa_recommendation="Re-run extraction or fill in manually."
    )

async def run_refine_agent(current_data: schemas.ComplaintBase, prompt_text: str) -> dict:
    """Refine existing data based on a new prompt."""
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        # Mock response
        return {
            "extracted_data": current_data,
            "risk_analysis": schemas.RiskAssessmentBase(
                risk_class="Updated Risk",
                root_cause_hypothesis="Updated root cause due to mock.",
                capa_recommendation="Updated CAPA recommendation."
            )
        }

    refiner = structured_llm(schemas.ComplaintBase)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert pharmaceutical Quality Assurance assistant. "
                   "Given the current complaint details in JSON, apply the user's instructions to update the details. "
                   "Keep all other details exactly the same. Return the updated structured data."),
        ("human", "Current Data:\n{current_data}\n\nUser Instruction:\n{instruction}")
    ])
    
    chain = prompt | refiner
    
    try:
        updated_data = await chain.ainvoke({
            "current_data": current_data.model_dump_json(),
            "instruction": prompt_text
        })
        updated_data = normalize_extracted(updated_data)
    except Exception as e:
        raise Exception(f"Refinement failed: {str(e)}")

    state = {"complaint_text": "", "extracted_data": updated_data, "errors": None}
    risk_result = assess_risk(state)
    if risk_result.get("errors"):
        raise Exception(risk_result["errors"])
        
    return {
        "extracted_data": updated_data,
        "risk_analysis": risk_result.get("risk_analysis") or _risk_unavailable()
    }
