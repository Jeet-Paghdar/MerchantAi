from datetime import datetime
from typing import Any, Dict, Optional
from database import AsyncSessionLocal
from audit.models import AuditLog

class AuditLogger:
    @staticmethod
    async def log(session_id: str, action_type: str, actor: str, reasoning: str, input_data: Optional[Dict[str, Any]] = None, output_data: Optional[Dict[str, Any]] = None, bounds_check: Optional[Dict[str, Any]] = None, gate_check: Optional[Dict[str, Any]] = None, razorpay_api_call: Optional[Dict[str, Any]] = None, status: str = "success", error_message: Optional[str] = None):
        async with AsyncSessionLocal() as session:
            entry = AuditLog(
                timestamp=datetime.utcnow(),
                session_id=session_id,
                action_type=action_type,
                actor=actor,
                reasoning=reasoning,
                input_data=input_data,
                output_data=output_data,
                bounds_check=bounds_check,
                gate_check=gate_check,
                razorpay_api_call=razorpay_api_call,
                status=status,
                error_message=error_message
            )
            session.add(entry)
            await session.commit()