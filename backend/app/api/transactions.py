"""
Transaction ingestion endpoint.

POST /api/v1/transaction — ingest a single transaction
POST /api/v1/transaction/batch — ingest a batch
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.transaction import TransactionIn, TransactionOut, TransactionBatchIn
from app.services.ingestion_service import IngestionService
from app.services.fraud_detection import FraudDetectionService

router = APIRouter(prefix="/transaction", tags=["transactions"])


@router.post("", response_model=TransactionOut)
async def ingest_transaction(
    txn: TransactionIn,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a single transaction.

    - Hashes all PII fields (account, merchant, device)
    - Adds nodes and edges to the transaction graph
    - Runs fraud detection rules
    - Returns the sanitized transaction record
    """
    # Ingest into graph
    ingestion = IngestionService()
    result = ingestion.ingest(txn)

    # Run fraud detection rules
    fraud = FraudDetectionService()
    alerts = await fraud.run_all_rules(db, result.account_hash, result.device_hash)
    result.alerts_generated = len(alerts)

    return result


@router.post("/batch", response_model=list[TransactionOut])
async def ingest_batch(
    batch: TransactionBatchIn,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a batch of transactions.
    Each transaction is processed individually for fraud detection.
    """
    ingestion = IngestionService()
    fraud = FraudDetectionService()
    results = []

    for txn in batch.transactions:
        result = ingestion.ingest(txn)
        alerts = await fraud.run_all_rules(db, result.account_hash, result.device_hash)
        result.alerts_generated = len(alerts)
        results.append(result)

    return results
