"""
Debugging aid: lists the Groq models this API key can actually use, then
smoke-tests structured output (tool calling) on the one configured in
agent/graph.py. Run from backend/ with the venv active:  python test_models.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from langchain_groq import ChatGroq
import schemas

SAMPLE = ("Email from John Doe: We received batch B12345 of Paracetamol 500mg today. "
          "Around 100kg of the tablets were crushed and broken. Please investigate. "
          "Severity is critical.")

print("Models available on this account:")
for m in sorted(m.id for m in Groq().models.list().data):
    print("  -", m)

model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
print(f"\nStructured-output smoke test with {model}:")
try:
    llm = ChatGroq(model=model, temperature=0).with_structured_output(schemas.ComplaintBase)
    res = llm.invoke("Extract complaint details: " + SAMPLE)
    print("  OK ->", {k: v for k, v in res.model_dump().items() if v is not None})
except Exception as e:
    print(f"  FAILED: {e}")
