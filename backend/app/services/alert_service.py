"""
Alert CRUD service.
"""

import json
from typing import Optional
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert


class AlertService:
    """Manages alert persistence and retrieval."""

    @staticmethod
    async def get_alerts(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[Alert], int]:
        """Get paginated alerts with optional filters."""
        query = select(Alert)

        if severity:
            query = query.where(Alert.severity == severity)
        if alert_type:
            query = query.where(Alert.alert_type == alert_type)
        if status:
            query = query.where(Alert.status == status)

        # Total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # Paginated results, newest first
        query = query.order_by(desc(Alert.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        alerts = result.scalars().all()

        return list(alerts), total

    @staticmethod
    async def get_alert(db: AsyncSession, alert_id: int) -> Optional[Alert]:
        """Get a single alert by ID."""
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_verdict(
        db: AsyncSession, alert_id: int, verdict: str, notes: Optional[str] = None
    ) -> Optional[Alert]:
        """Update an alert's status with analyst verdict."""
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            return None

        alert.status = verdict
        if notes:
            existing = json.loads(alert.details or "{}")
            existing["analyst_notes"] = notes
            alert.details = json.dumps(existing)

        await db.commit()
        await db.refresh(alert)
        return alert

    @staticmethod
    async def get_stats(db: AsyncSession) -> dict:
        """Get alert statistics for the dashboard."""
        # Total alerts
        total = (await db.execute(select(func.count(Alert.id)))).scalar() or 0

        # By severity
        severity_counts = {}
        for sev in ["critical", "high", "medium", "low"]:
            count = (
                await db.execute(
                    select(func.count(Alert.id)).where(Alert.severity == sev)
                )
            ).scalar() or 0
            severity_counts[sev] = count

        # By type
        type_counts = {}
        for atype in ["shared_device", "velocity", "fan_out", "cycle"]:
            count = (
                await db.execute(
                    select(func.count(Alert.id)).where(Alert.alert_type == atype)
                )
            ).scalar() or 0
            type_counts[atype] = count

        # Recent alerts
        recent_query = (
            select(Alert)
            .order_by(desc(Alert.created_at))
            .limit(5)
        )
        recent_result = await db.execute(recent_query)
        recent = recent_result.scalars().all()

        return {
            "total_alerts": total,
            "alerts_by_severity": severity_counts,
            "alerts_by_type": type_counts,
            "recent_alerts": [
                {
                    "id": a.id,
                    "alert_type": a.alert_type,
                    "severity": a.severity,
                    "risk_score": a.risk_score,
                    "description": a.description[:100],
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in recent
            ],
        }
