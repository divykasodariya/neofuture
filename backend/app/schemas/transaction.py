"""
Pydantic schemas for transaction ingestion.
"""

from pydantic import BaseModel, Field
from typing import Optional


class TransactionIn(BaseModel):
    """Raw transaction event from the source system."""

    # PII fields — will be hashed before storage
    account_number: str = Field(..., description="Raw account number (will be hashed)")
    merchant_id: str = Field(..., description="Raw merchant ID (will be hashed)")
    device_fingerprint: str = Field(..., description="Device fingerprint (will be hashed)")

    # Transaction details — stored as-is
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    channel: str = Field(default="web", description="Channel: web, pos, atm, mobile")
    merchant_category: str = Field(default="general", description="Merchant category code")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp (auto-generated if empty)")


class TransactionOut(BaseModel):
    """Response after successful ingestion."""

    tx_id: str
    account_hash: str
    merchant_hash: str
    device_hash: str
    amount: float
    currency: str
    channel: str
    merchant_category: str
    timestamp: str
    alerts_generated: int = 0


class TransactionBatchIn(BaseModel):
    """Batch of transactions for bulk ingestion."""
    transactions: list[TransactionIn]
