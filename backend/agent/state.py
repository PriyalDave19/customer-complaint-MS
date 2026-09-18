from typing import TypedDict, Annotated, Optional
import schemas

class AgentState(TypedDict):
    complaint_text: str
    extracted_data: Optional[schemas.ComplaintBase]
    risk_analysis: Optional[schemas.RiskAssessmentBase]
    errors: Optional[str]
