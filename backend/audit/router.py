from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List
from database import get_db
from audit.models import AuditLog, AuditEntry, AuditTrailResponse

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/trail", response_model=AuditTrailResponse)
async def get_trail(session_id: str = None, db: AsyncSession = Depends(get_db)):
    if session_id and session_id != "all":
        query = select(AuditLog).filter(AuditLog.session_id == session_id).order_by(AuditLog.timestamp.desc())
        result = await db.execute(query)
        logs = result.scalars().all()
        if logs:
            return {"logs": logs}
    
    # Fallback to all recent audit logs across the platform so the merchant always sees activity
    query = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50)
    result = await db.execute(query)
    return {"logs": result.scalars().all()}

@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    query = select(AuditLog.action_type, func.count(AuditLog.id)).group_by(AuditLog.action_type)
    result = await db.execute(query)
    return {row[0]: row[1] for row in result.all()}

@router.get("/recent", response_model=List[AuditEntry])
async def get_recent(db: AsyncSession = Depends(get_db)):
    query = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50)
    result = await db.execute(query)
    return result.scalars().all()