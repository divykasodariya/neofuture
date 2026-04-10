"""
Graph query service.

Wraps the graph store for API consumption — subgraph extraction,
node properties, and Cytoscape.js format conversion.
"""

from app.core.graph_store import get_graph_store


class GraphService:
    """Graph query interface for the API layer."""

    def __init__(self):
        self.graph = get_graph_store()

    def get_subgraph(self, node_id: str, hops: int = 2) -> dict:
        """
        Get N-hop neighborhood of a node.
        Returns Cytoscape.js elements format.
        """
        return self.graph.get_subgraph(node_id, hops=hops)

    def get_node_info(self, node_id: str) -> dict | None:
        """Get properties of a single node."""
        if not self.graph.graph.has_node(node_id):
            return None

        data = dict(self.graph.graph.nodes[node_id])
        data["id"] = node_id

        # Add computed properties
        node_type = data.get("node_type")
        if node_type == "account":
            data["merchant_count"] = len(self.graph.get_account_merchants(node_id))
            data["transaction_count"] = len(self.graph.get_account_transactions(node_id))
        elif node_type == "device":
            data["linked_accounts"] = len(self.graph.get_device_accounts(node_id))

        return data

    def get_full_graph_summary(self) -> dict:
        """Summary stats about the entire graph."""
        counts = self.graph.node_count()
        return {
            "total_nodes": sum(counts.values()),
            "total_edges": self.graph.edge_count(),
            **counts,
        }

    def search_nodes(self, query: str, node_type: str | None = None, limit: int = 20) -> list[dict]:
        """Search for nodes by partial ID match."""
        results = []
        for node_id, data in self.graph.graph.nodes(data=True):
            if node_type and data.get("node_type") != node_type:
                continue
            if query.lower() in node_id.lower() or query.lower() in data.get("label", "").lower():
                result = dict(data)
                result["id"] = node_id
                results.append(result)
                if len(results) >= limit:
                    break
        return results
