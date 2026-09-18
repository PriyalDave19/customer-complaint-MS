from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import engine, get_db, Base
import models
import schemas
from agent.graph import run_agent

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIVOA QMS API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, in prod use exact domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AIVOA QMS API is running"}

@app.post("/api/complaints/extract", response_model=schemas.ExtractionResponse)
async def extract_complaint(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Endpoint to process complaint text or file using LangGraph.
    """
    if not text and not file:
        raise HTTPException(status_code=400, detail="Must provide text or file")
    
    content = text
    if file:
        # In a real app, use PyPDF2 or similar OCR for PDFs
        # For this demo, we assume the file is a text file or we just use the text input
        content = await file.read()
        content = content.decode('utf-8')
    
    # Run LangGraph Agent
    result = await run_agent(content)
    
    return result

@app.post("/api/complaints/", response_model=schemas.ComplaintResponse)
def create_complaint(complaint: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    """
    Endpoint to save a complaint to the database.
    """
    db_complaint = models.Complaint(**complaint.dict(exclude={"risk_assessment"}))
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    
    if complaint.risk_assessment:
        db_risk = models.RiskAssessment(
            complaint_id=db_complaint.id,
            **complaint.risk_assessment.dict()
        )
        db.add(db_risk)
        db.commit()
        db.refresh(db_risk)
        
    return db_complaint

@app.get("/api/complaints/", response_model=List[schemas.ComplaintResponse])
def get_complaints(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    complaints = db.query(models.Complaint).offset(skip).limit(limit).all()
    return complaints

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
