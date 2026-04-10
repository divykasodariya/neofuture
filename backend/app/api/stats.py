"""
Dashboard statistics endpoint.

GET /api/v1/stats — overview metrics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.alert_service import AlertService
from app.services.graph_service import GraphService

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Get dashboard overview metrics:
    - Graph stats (nodes, edges by type)
    - Alert stats (by severity, by type)
    - Recent alerts
    """
    graph_service = GraphService()
    graph_stats = graph_service.get_full_graph_summary()
    alert_stats = await AlertService.get_stats(db)

    return {
        "graph": graph_stats,
        "alerts": alert_stats,
    }
