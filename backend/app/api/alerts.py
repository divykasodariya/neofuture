"""
Alert endpoints.

GET /api/v1/alerts — paginated alert list
GET /api/v1/alerts/{id} — single alert detail
POST /api/v1/alerts/{id}/verdict — analyst verdict
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.schemas.alert import AlertOut, AlertListOut, VerdictIn
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertListOut)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated alert feed with optional filters."""
    alerts, total = await AlertService.get_alerts(
        db, page=page, page_size=page_size,
        severity=severity, alert_type=alert_type, status=status,
    )
    return AlertListOut(
        alerts=[AlertOut.model_validate(a) for a in alerts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single alert by ID, including explanation."""
    alert = await AlertService.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertOut.model_validate(alert)


@router.post("/{alert_id}/verdict", response_model=AlertOut)
async def submit_verdict(
    alert_id: int,
    verdict: VerdictIn,
    db: AsyncSession = Depends(get_db),
):
    """Submit analyst verdict on an alert."""
    if verdict.verdict not in ("confirmed", "false_positive", "escalated"):
        raise HTTPException(
            status_code=400,
            detail="Verdict must be: confirmed, false_positive, or escalated"
        )

    alert = await AlertService.update_verdict(
        db, alert_id, verdict.verdict, verdict.notes
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertOut.model_validate(alert)
