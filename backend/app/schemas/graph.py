"""
Pydantic schemas for graph API responses.
"""

from pydantic import BaseModel
from typing import Any, Optional


class GraphNode(BaseModel):
    """A single graph node in Cytoscape format."""
    data: dict[str, Any]


class GraphEdge(BaseModel):
    """A single graph edge in Cytoscape format."""
    data: dict[str, Any]


class SubgraphOut(BaseModel):
    """Subgraph response — Cytoscape.js elements format."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    center_node: str
    hops: int


class StatsOut(BaseModel):
    """Dashboard statistics."""
    total_transactions: int
    total_accounts: int
    total_merchants: int
    total_devices: int
    total_alerts: int
    alerts_by_severity: dict[str, int]
    alerts_by_type: dict[str, int]
    recent_alerts: list[dict[str, Any]]
