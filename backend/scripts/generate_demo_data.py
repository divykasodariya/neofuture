#!/usr/bin/env python3
"""
Synthetic transaction data generator for zkTransact demo.

Generates realistic transaction patterns including:
- Normal users with regular spending
- Fraud rings: coordinated accounts sharing devices
- Mule accounts: routing money through multiple merchants
- Velocity attacks: burst transactions
"""

import asyncio
import sys
import os
import json
import random
from datetime import datetime, timedelta, timezone

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import init_db, async_session
from app.services.ingestion_service import IngestionService
from app.services.fraud_detection import FraudDetectionService
from app.schemas.transaction import TransactionIn
from app.core.graph_store import get_graph_store


# --- Configuration ---
NUM_NORMAL_ACCOUNTS = 15
NUM_FRAUD_RING_ACCOUNTS = 6
NUM_MULE_ACCOUNTS = 3
NUM_NORMAL_MERCHANTS = 10
NUM_DEVICES = 12
NORMAL_TXN_PER_ACCOUNT = 5

MERCHANT_CATEGORIES = [
    "grocery", "electronics", "restaurant", "gas_station",
    "clothing", "pharmacy", "travel", "entertainment",
    "online_retail", "utility",
]

CHANNELS = ["web", "pos", "atm", "mobile"]
CURRENCIES = ["USD"]


def random_timestamp(hours_ago_max: int = 72) -> str:
    """Generate a random timestamp within the last N hours."""
    offset = random.randint(0, hours_ago_max * 3600)
    ts = datetime.now(timezone.utc) - timedelta(seconds=offset)
    return ts.isoformat()


def recent_timestamp(minutes_ago_max: int = 30) -> str:
    """Generate a very recent timestamp (for velocity attacks)."""
    offset = random.randint(0, minutes_ago_max * 60)
    ts = datetime.now(timezone.utc) - timedelta(seconds=offset)
    return ts.isoformat()


def generate_normal_transactions() -> list[TransactionIn]:
    """Generate normal user transaction patterns."""
    txns = []
    for i in range(NUM_NORMAL_ACCOUNTS):
        account = f"ACC-NORMAL-{i:04d}"
        device = f"DEV-{random.randint(0, NUM_DEVICES - 1):04d}"

        for _ in range(random.randint(2, NORMAL_TXN_PER_ACCOUNT)):
            merchant = f"MERCH-{random.randint(0, NUM_NORMAL_MERCHANTS - 1):04d}"
            txns.append(TransactionIn(
                account_number=account,
                merchant_id=merchant,
                device_fingerprint=device,
                amount=round(random.uniform(5.0, 500.0), 2),
                currency="USD",
                channel=random.choice(CHANNELS),
                merchant_category=random.choice(MERCHANT_CATEGORIES),
                timestamp=random_timestamp(72),
            ))
    return txns


def generate_fraud_ring() -> list[TransactionIn]:
    """
    Generate a fraud ring pattern:
    - Multiple accounts share 1-2 devices
    - They transact at overlapping merchants
    - Circular money flow pattern
    """
    txns = []
    # Shared devices — the key signal
    shared_device_1 = "DEV-FRAUD-RING-001"
    shared_device_2 = "DEV-FRAUD-RING-002"
    ring_devices = [shared_device_1, shared_device_2]

    ring_accounts = [f"ACC-RING-{i:04d}" for i in range(NUM_FRAUD_RING_ACCOUNTS)]
    ring_merchants = [f"MERCH-RING-{i:04d}" for i in range(4)]

    # Each ring account transacts using shared devices
    for account in ring_accounts:
        device = random.choice(ring_devices)
        for merchant in random.sample(ring_merchants, k=random.randint(2, 4)):
            txns.append(TransactionIn(
                account_number=account,
                merchant_id=merchant,
                device_fingerprint=device,
                amount=round(random.uniform(100.0, 2000.0), 2),
                currency="USD",
                channel="web",
                merchant_category="online_retail",
                timestamp=random_timestamp(24),
            ))

    # Cross-ring transactions (account A → merchant → account B pattern)
    for i in range(len(ring_accounts) - 1):
        txns.append(TransactionIn(
            account_number=ring_accounts[i],
            merchant_id=f"MERCH-TRANSFER-{i:04d}",
            device_fingerprint=shared_device_1,
            amount=round(random.uniform(500.0, 5000.0), 2),
            currency="USD",
            channel="web",
            merchant_category="online_retail",
            timestamp=recent_timestamp(60),
        ))

    return txns


def generate_mule_accounts() -> list[TransactionIn]:
    """
    Generate mule account patterns:
    - One account with very high merchant diversity
    - Many small transactions (structuring)
    """
    txns = []
    for i in range(NUM_MULE_ACCOUNTS):
        account = f"ACC-MULE-{i:04d}"
        device = f"DEV-MULE-{i:04d}"

        # Many merchants — structuring signal
        for j in range(8):
            txns.append(TransactionIn(
                account_number=account,
                merchant_id=f"MERCH-SPREAD-{j:04d}",
                device_fingerprint=device,
                amount=round(random.uniform(50.0, 300.0), 2),
                currency="USD",
                channel=random.choice(["web", "pos"]),
                merchant_category=random.choice(MERCHANT_CATEGORIES),
                timestamp=random_timestamp(12),
            ))

    return txns


def generate_velocity_attack() -> list[TransactionIn]:
    """
    Generate velocity attack pattern:
    - One account, many transactions in a very short window
    """
    txns = []
    account = "ACC-VELOCITY-0001"
    device = "DEV-VELOCITY-0001"

    for i in range(15):
        txns.append(TransactionIn(
            account_number=account,
            merchant_id=f"MERCH-{random.randint(0, 5):04d}",
            device_fingerprint=device,
            amount=round(random.uniform(10.0, 100.0), 2),
            currency="USD",
            channel="web",
            merchant_category="online_retail",
            timestamp=recent_timestamp(15),  # All within 15 minutes
        ))

    return txns


async def seed():
    """Run the full seeding pipeline."""
    print("=" * 60)
    print("  zkTransact — Demo Data Generator")
    print("=" * 60)

    # Initialize DB
    await init_db()
    print("\n✓ Database initialized")

    # Clear existing graph
    graph = get_graph_store()
    graph.clear()
    print("✓ Graph cleared")

    # Generate all transaction sets
    all_txns = []

    normal = generate_normal_transactions()
    all_txns.extend(normal)
    print(f"✓ Generated {len(normal)} normal transactions")

    ring = generate_fraud_ring()
    all_txns.extend(ring)
    print(f"✓ Generated {len(ring)} fraud ring transactions")

    mule = generate_mule_accounts()
    all_txns.extend(mule)
    print(f"✓ Generated {len(mule)} mule account transactions")

    velocity = generate_velocity_attack()
    all_txns.extend(velocity)
    print(f"✓ Generated {len(velocity)} velocity attack transactions")

    # Shuffle for realism
    random.shuffle(all_txns)

    # Ingest all transactions
    ingestion = IngestionService()
    fraud = FraudDetectionService()
    total_alerts = 0

    print(f"\n▶ Ingesting {len(all_txns)} transactions...")

    async with async_session() as db:
        for i, txn in enumerate(all_txns):
            result = ingestion.ingest(txn)
            alerts = await fraud.run_all_rules(db, result.account_hash, result.device_hash)
            total_alerts += len(alerts)

            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(all_txns)} transactions...")

    # Print summary
    counts = graph.node_count()
    print(f"\n{'=' * 60}")
    print(f"  Seeding Complete!")
    print(f"{'=' * 60}")
    print(f"  Transactions ingested: {len(all_txns)}")
    print(f"  Account nodes:         {counts.get('account', 0)}")
    print(f"  Merchant nodes:        {counts.get('merchant', 0)}")
    print(f"  Device nodes:          {counts.get('device', 0)}")
    print(f"  Total edges:           {graph.edge_count()}")
    print(f"  Alerts generated:      {total_alerts}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(seed())
