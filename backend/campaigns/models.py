from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import Base
import enum

class CampaignStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    expired = "expired"

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    status = Column(Enum(CampaignStatus), default=CampaignStatus.active)
    escalation_level = Column(Integer, default=1)
    messages = Column(JSON, default=list)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_escalation_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class CampaignStats(BaseModel):
    total_carts: int
    recovered: int
    recovery_rate: float
    active_campaigns: int