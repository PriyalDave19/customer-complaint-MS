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

class ComplaintBase(BaseModel):
    source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity_affected: Optional[float] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None

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
