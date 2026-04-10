"""
Graph exploration endpoints.

GET /api/v1/graph/{node_id} — N-hop subgraph
GET /api/v1/graph/{node_id}/info — node properties
GET /api/v1/graph/search — search nodes
GET /api/v1/graph/summary — graph overview
"""

from fastapi import APIRouter, Query, HTTPException

from app.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/summary")
async def graph_summary():
    """Get overall graph statistics."""
    service = GraphService()
    return service.get_full_graph_summary()


@router.get("/search")
async def search_nodes(
    q: str = Query(..., min_length=1),
    node_type: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """Search for nodes by partial ID match."""
    service = GraphService()
    return service.search_nodes(q, node_type=node_type, limit=limit)


@router.get("/{node_id}")
async def get_subgraph(
    node_id: str,
    hops: int = Query(2, ge=1, le=4),
):
    """
    Get N-hop neighborhood of a node in Cytoscape.js format.
    This is the core endpoint for the graph explorer.
    """
    service = GraphService()
    subgraph = service.get_subgraph(node_id, hops=hops)

    if not subgraph["nodes"]:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in graph")

    return {
        "elements": subgraph,
        "center_node": node_id,
        "hops": hops,
    }


@router.get("/{node_id}/info")
async def get_node_info(node_id: str):
    """Get detailed properties of a single node."""
    service = GraphService()
    info = service.get_node_info(node_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return info
