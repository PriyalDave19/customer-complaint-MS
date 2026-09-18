from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

# --- Data Schemas for DB ---
class RiskAssessmentBase(BaseModel):
    risk_class: Optional[str] = None
    root_cause_hypothesis: Optional[str] = None
    capa_recommendation: Optional[str] = None

class RiskAssessmentCreate(RiskAssessmentBase):
    pass

class RiskAssessmentResponse(RiskAssessmentBase):
    id: int
    complaint_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Allowed values for the form's <select> controls (frontend ComplaintForm.tsx).
# Extracted values are normalised to these in agent/graph.py so the dropdowns
# actually display what the AI picked.
SEVERITY_OPTIONS = ["Critical", "Major", "Minor"]
PRIORITY_OPTIONS = ["High", "Medium", "Low"]
DATE_FORMAT_HINT = "ISO date YYYY-MM-DD (the form uses a date picker), or null"

class ComplaintBase(BaseModel):
    source: Optional[str] = Field(None, description="Channel the complaint came in on, e.g. Email, Phone, Web Form, Letter")
    customer_name: Optional[str] = None
    product_name: Optional[str] = Field(None, description="Product name only, without the strength (e.g. 'Paracetamol')")
    product_strength: Optional[str] = Field(None, description="Strength or grade, e.g. '500mg'")
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = Field(None, description=DATE_FORMAT_HINT)
    expiry_date: Optional[str] = Field(None, description=DATE_FORMAT_HINT)
    quantity_affected: Optional[float] = Field(None, description="Numeric quantity affected (in kg or units), number only")
    complaint_type: Optional[str] = Field(None, description="Short category, e.g. Packaging Defect, Physical Defect, Contamination, Labeling Error, Efficacy")
    complaint_date: Optional[str] = Field(None, description=DATE_FORMAT_HINT)
    description: Optional[str] = None
    severity: Optional[str] = Field(None, description=f"One of exactly: {', '.join(SEVERITY_OPTIONS)}. Map 'high'/'severe' to Critical, 'moderate' to Major, 'low' to Minor.")
    priority: Optional[str] = Field(None, description=f"One of exactly: {', '.join(PRIORITY_OPTIONS)}")

class ComplaintCreate(ComplaintBase):
    risk_assessment: Optional[RiskAssessmentCreate] = None

class ComplaintResponse(ComplaintBase):
    id: int
    created_at: datetime.datetime
    risk_assessment: Optional[RiskAssessmentResponse] = None

    class Config:
        from_attributes = True

# --- Schemas for AI Extraction Response ---
class ExtractionResponse(BaseModel):
    extracted_data: ComplaintBase
    risk_analysis: RiskAssessmentBase

class RefineRequest(BaseModel):
    current_data: ComplaintBase
    prompt: str
