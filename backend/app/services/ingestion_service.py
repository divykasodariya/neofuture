"""
Transaction ingestion service.

Receives raw transaction events, hashes all PII, and inserts
nodes + edges into the in-memory graph.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.hashing import hash_account, hash_merchant, hash_device
from app.core.graph_store import get_graph_store
from app.schemas.transaction import TransactionIn, TransactionOut
from app.models.transaction import Transaction


class IngestionService:
    """Processes raw transaction events into the graph."""

    def __init__(self):
        self.graph = get_graph_store()

    async def ingest(self, db: AsyncSession, txn: TransactionIn) -> TransactionOut:
        """
        Process a single transaction:
        1. Hash all PII fields
        2. Generate a transaction ID
        3. Add nodes and edges to the graph
        4. Return the sanitized transaction record
        """
        # Step 1: Hash PII — raw values never persist
        account_hash = hash_account(txn.account_number)
        merchant_hash = hash_merchant(txn.merchant_id)
        device_hash = hash_device(txn.device_fingerprint)

        # Step 2: Generate transaction ID
        tx_id = f"tx_{uuid.uuid4().hex[:16]}"

        # Step 3: Timestamp
        timestamp = txn.timestamp or datetime.now(timezone.utc).isoformat()

        # Step 4: Add to graph
        self.graph.add_transaction(
            tx_id=tx_id,
            account_hash=account_hash,
            merchant_hash=merchant_hash,
            device_hash=device_hash,
            amount=txn.amount,
            currency=txn.currency,
            channel=txn.channel,
            merchant_category=txn.merchant_category,
            timestamp=timestamp,
        )

        # Step 5: Save to database
        db_txn = Transaction(
            tx_id=tx_id,
            account_hash=account_hash,
            merchant_hash=merchant_hash,
            device_hash=device_hash,
            amount=txn.amount,
            currency=txn.currency,
            channel=txn.channel,
            merchant_category=txn.merchant_category,
            timestamp=timestamp,
        )
        db.add(db_txn)
        await db.commit()

        return TransactionOut(
            tx_id=tx_id,
            account_hash=account_hash,
            merchant_hash=merchant_hash,
            device_hash=device_hash,
            amount=txn.amount,
            currency=txn.currency,
            channel=txn.channel,
            merchant_category=txn.merchant_category,
            timestamp=timestamp,
        )

    async def ingest_batch(self, db: AsyncSession, transactions: list[TransactionIn]) -> list[TransactionOut]:
        """Process a batch of transactions."""
        results = []
        for txn in transactions:
            results.append(await self.ingest(db, txn))
        return results
