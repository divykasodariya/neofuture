"""
In-memory graph store using NetworkX.

This is the central graph that holds all transaction relationships.
In production, swap this for Neo4j — the service interface stays identical.
"""

import networkx as nx
from datetime import datetime
from typing import Any
import threading


class GraphStore:
    """Thread-safe singleton NetworkX graph store."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._graph = nx.MultiDiGraph()
        return cls._instance

    @property
    def graph(self) -> nx.MultiDiGraph:
        return self._graph

    def add_account_node(self, account_hash: str) -> None:
        """Add or update an account node."""
        if not self._graph.has_node(account_hash):
            self._graph.add_node(
                account_hash,
                node_type="account",
                label=f"acct_{account_hash[:8]}",
                created_at=datetime.utcnow().isoformat(),
                transaction_count=0,
            )

    def add_merchant_node(self, merchant_hash: str, category: str = "unknown") -> None:
        """Add or update a merchant node."""
        if not self._graph.has_node(merchant_hash):
            self._graph.add_node(
                merchant_hash,
                node_type="merchant",
                label=f"merch_{merchant_hash[:8]}",
                category=category,
                created_at=datetime.utcnow().isoformat(),
            )

    def add_device_node(self, device_hash: str) -> None:
        """Add or update a device node."""
        if not self._graph.has_node(device_hash):
            self._graph.add_node(
                device_hash,
                node_type="device",
                label=f"dev_{device_hash[:8]}",
                created_at=datetime.utcnow().isoformat(),
            )

    def add_transaction(
        self,
        tx_id: str,
        account_hash: str,
        merchant_hash: str,
        device_hash: str,
        amount: float,
        currency: str,
        channel: str,
        merchant_category: str,
        timestamp: str,
    ) -> None:
        """
        Add a full transaction to the graph, creating all nodes and edges.
        """
        # Ensure all nodes exist
        self.add_account_node(account_hash)
        self.add_merchant_node(merchant_hash, category=merchant_category)
        self.add_device_node(device_hash)

        # Update account transaction count
        self._graph.nodes[account_hash]["transaction_count"] = (
            self._graph.nodes[account_hash].get("transaction_count", 0) + 1
        )

        # Add edges
        # Account → Merchant (TRANSACTED_AT)
        self._graph.add_edge(
            account_hash,
            merchant_hash,
            edge_type="TRANSACTED_AT",
            tx_id=tx_id,
            amount=amount,
            currency=currency,
            channel=channel,
            timestamp=timestamp,
        )

        # Account → Device (USED_DEVICE)
        # Only add if not already linked
        has_device_link = any(
            d.get("edge_type") == "USED_DEVICE"
            for _, _, d in self._graph.edges(account_hash, data=True)
            if _ == account_hash and self._graph.has_edge(account_hash, device_hash)
        )
        if not has_device_link:
            self._graph.add_edge(
                account_hash,
                device_hash,
                edge_type="USED_DEVICE",
            )

    def get_subgraph(self, node_id: str, hops: int = 2) -> dict[str, Any]:
        """
        Get N-hop neighborhood of a node in Cytoscape.js format.
        """
        if not self._graph.has_node(node_id):
            return {"nodes": [], "edges": []}

        # BFS to get N-hop neighbors
        visited = {node_id}
        frontier = {node_id}

        for _ in range(hops):
            next_frontier = set()
            for n in frontier:
                # Get both successors and predecessors
                next_frontier.update(self._graph.successors(n))
                next_frontier.update(self._graph.predecessors(n))
            next_frontier -= visited
            visited.update(next_frontier)
            frontier = next_frontier

        # Build Cytoscape elements
        nodes = []
        for n in visited:
            data = dict(self._graph.nodes[n])
            data["id"] = n
            nodes.append({"data": data})

        edges = []
        edge_id = 0
        for u, v, d in self._graph.edges(data=True):
            if u in visited and v in visited:
                edge_data = dict(d)
                edge_data["id"] = f"e{edge_id}"
                edge_data["source"] = u
                edge_data["target"] = v
                edges.append({"data": edge_data})
                edge_id += 1

        return {"nodes": nodes, "edges": edges}

    def get_device_accounts(self, device_hash: str) -> list[str]:
        """Get all accounts linked to a device."""
        accounts = []
        for pred in self._graph.predecessors(device_hash):
            node_data = self._graph.nodes.get(pred, {})
            if node_data.get("node_type") == "account":
                accounts.append(pred)
        return accounts

    def get_account_merchants(self, account_hash: str) -> list[str]:
        """Get all merchants an account has transacted with."""
        merchants = []
        for succ in self._graph.successors(account_hash):
            node_data = self._graph.nodes.get(succ, {})
            if node_data.get("node_type") == "merchant":
                merchants.append(succ)
        return merchants

    def get_account_transactions(self, account_hash: str) -> list[dict]:
        """Get all transaction edges from an account."""
        txns = []
        for _, target, data in self._graph.edges(account_hash, data=True):
            if data.get("edge_type") == "TRANSACTED_AT":
                txn = dict(data)
                txn["merchant"] = target
                txns.append(txn)
        return txns

    def get_all_accounts(self) -> list[str]:
        """Get all account node IDs."""
        return [
            n for n, d in self._graph.nodes(data=True)
            if d.get("node_type") == "account"
        ]

    def get_all_devices(self) -> list[str]:
        """Get all device node IDs."""
        return [
            n for n, d in self._graph.nodes(data=True)
            if d.get("node_type") == "device"
        ]

    def find_cycles(self, max_length: int = 5) -> list[list[str]]:
        """Find cycles in the graph (money flow loops)."""
        try:
            # Only look at account-to-account paths through merchants
            simple = self._graph.to_undirected()
            cycles = list(nx.cycle_basis(simple))
            # Filter to reasonable length
            return [c for c in cycles if len(c) <= max_length]
        except Exception:
            return []

    def node_count(self) -> dict[str, int]:
        """Count nodes by type."""
        counts = {"account": 0, "merchant": 0, "device": 0}
        for _, data in self._graph.nodes(data=True):
            ntype = data.get("node_type", "unknown")
            counts[ntype] = counts.get(ntype, 0) + 1
        return counts

    def edge_count(self) -> int:
        """Total edge count."""
        return self._graph.number_of_edges()

    def clear(self) -> None:
        """Clear the entire graph (for testing)."""
        self._graph.clear()


# Singleton accessor
def get_graph_store() -> GraphStore:
    return GraphStore()
