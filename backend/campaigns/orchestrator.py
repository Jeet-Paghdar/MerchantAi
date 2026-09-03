from datetime import datetime, timedelta
from sqlalchemy.future import select
from sqlalchemy import func
from database import AsyncSessionLocal
from checkout.models import Cart, Order
from campaigns.models import Campaign, CampaignStatus
from audit.logger import AuditLogger

class CampaignOrchestrator:
    async def check_abandoned_carts(self):
        async with AsyncSessionLocal() as db:
            threshold = datetime.utcnow() - timedelta(minutes=30)
            # Find carts updated before threshold with no order
            carts = (await db.execute(select(Cart).filter(Cart.updated_at < threshold))).scalars().all()
            for cart in carts:
                order = (await db.execute(select(Order).filter(Order.cart_id == cart.id))).scalars().first()
                if not order:
                    camp = (await db.execute(select(Campaign).filter(Campaign.cart_id == cart.id))).scalars().first()
                    if not camp:
                        camp = Campaign(session_id=cart.session_id, cart_id=cart.id)
                        db.add(camp)
                        await AuditLogger.log(cart.session_id, "CAMPAIGN_TRIGGERED", "system", "Started cart recovery campaign")
            await db.commit()

    async def escalate(self, campaign_id: int):
        async with AsyncSessionLocal() as db:
            camp = await db.get(Campaign, campaign_id)
            if not camp or camp.status != CampaignStatus.active: return
            
            levels = {1: 'gentle reminder', 2: 'urgency/scarcity', 3: 'discount offer'}
            
            if camp.escalation_level < 3:
                camp.escalation_level += 1
                camp.last_escalation_at = datetime.utcnow()
                msg = f"Escalation {camp.escalation_level}: {levels[camp.escalation_level]}"
                
                msgs = list(camp.messages)
                msgs.append(msg)
                camp.messages = msgs
                
                await AuditLogger.log(camp.session_id, "CAMPAIGN_TRIGGERED", "system", f"Escalated to level {camp.escalation_level}")
            else:
                camp.status = CampaignStatus.expired
            await db.commit()

    async def get_dashboard_stats(self) -> dict:
        async with AsyncSessionLocal() as db:
            total = (await db.execute(select(func.count(Campaign.id)))).scalar()
            recovered = (await db.execute(select(func.count(Campaign.id)).filter(Campaign.status == CampaignStatus.completed))).scalar()
            active = (await db.execute(select(func.count(Campaign.id)).filter(Campaign.status == CampaignStatus.active))).scalar()
            rate = (recovered / total * 100) if total > 0 else 0.0
            return {"total_carts": total, "recovered": recovered, "recovery_rate": rate, "active_campaigns": active}