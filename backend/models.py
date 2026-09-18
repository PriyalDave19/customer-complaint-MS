from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    
    # 1. ORIGIN & CUSTOMER DETAILS
    source = Column(String, index=True)
    customer_name = Column(String, index=True)
    
    # 2. PRODUCT & BATCH IDENTIFICATION
    product_name = Column(String, index=True)
    product_strength = Column(String)
    batch_number = Column(String, index=True)
    manufacturing_date = Column(String) # Storing as string for simplicity in demo
    expiry_date = Column(String)
    quantity_affected = Column(Float)
    
    # 3. COMPLAINT DETAILS
    complaint_type = Column(String)
    complaint_date = Column(String)
    description = Column(Text)
    
    # 4. INITIAL ASSESSMENT & PRIORITY
    severity = Column(String)
    priority = Column(String)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    risk_assessment = relationship("RiskAssessment", back_populates="complaint", uselist=False)

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"))
    
    # AI generated fields
    risk_class = Column(String) # e.g., Critical, Major, Minor
    root_cause_hypothesis = Column(Text)
    capa_recommendation = Column(Text)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    complaint = relationship("Complaint", back_populates="risk_assessment")
