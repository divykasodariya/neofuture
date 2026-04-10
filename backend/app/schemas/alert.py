"""
Pydantic schemas for alerts.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AlertOut(BaseModel):
    """Alert response schema."""

    id: int
    alert_type: str
    severity: str
    risk_score: float
    account_id: str
    description: str
    details: Optional[str] = None
    related_nodes: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertListOut(BaseModel):
    """Paginated alert list."""

    alerts: list[AlertOut]
    total: int
    page: int
    page_size: int


class VerdictIn(BaseModel):
    """Analyst verdict on an alert."""

    verdict: str  # confirmed, false_positive, escalated
    notes: Optional[str] = None
