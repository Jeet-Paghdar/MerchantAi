from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String, index=True)
    action_type = Column(String)
    actor = Column(String)
    reasoning = Column(String)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    bounds_check = Column(JSON, nullable=True)
    gate_check = Column(JSON, nullable=True)
    razorpay_api_call = Column(JSON, nullable=True)
    status = Column(String)
    error_message = Column(String, nullable=True)

class AuditEntry(BaseModel):
    id: int
    timestamp: datetime
    session_id: str
    action_type: str
    actor: str
    reasoning: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    bounds_check: Optional[Dict[str, Any]] = None
    gate_check: Optional[Dict[str, Any]] = None
    razorpay_api_call: Optional[Dict[str, Any]] = None
    status: str
    error_message: Optional[str] = None
    class Config:
        from_attributes = True

class AuditTrailResponse(BaseModel):
    logs: list[AuditEntry]