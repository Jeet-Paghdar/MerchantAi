"""
MerchantAI Autonomous Campaign Orchestrator
Monitors cart activity, detects abandoned checkouts, and dispatches
dynamic urgency nudges and bounded margin recovery offers.
"""
from campaigns.orchestrator import CampaignOrchestrator
from campaigns.models import Campaign, CampaignStatus

__all__ = ["CampaignOrchestrator", "Campaign", "CampaignStatus"]

