"""
Rule-based fraud detection engine.

Runs detection rules against the graph and generates alerts.
No ML required — pure graph topology analysis.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.graph_store import get_graph_store, GraphStore
from app.core.config import get_settings
from app.models.alert import Alert


class FraudDetectionService:
    """Runs fraud detection rules against the transaction graph."""

    def __init__(self):
        self.graph: GraphStore = get_graph_store()
        self.settings = get_settings()

    async def run_all_rules(self, db: AsyncSession, account_hash: str, device_hash: str) -> list[Alert]:
        """
        Run all detection rules for a given transaction context.
        Returns list of generated alerts.
        """
        alerts = []

        # Rule 1: Shared device detection
        alert = await self._check_shared_device(db, account_hash, device_hash)
        if alert:
            alerts.append(alert)

        # Rule 2: Velocity anomaly
        alert = await self._check_velocity(db, account_hash)
        if alert:
            alerts.append(alert)

        # Rule 3: Fan-out (too many merchants)
        alert = await self._check_fan_out(db, account_hash)
        if alert:
            alerts.append(alert)

        # Rule 4: Cycle detection (periodic, not per-transaction for performance)
        cycle_alerts = await self._check_cycles(db, account_hash)
        alerts.extend(cycle_alerts)

        return alerts

    async def _check_shared_device(
        self, db: AsyncSession, account_hash: str, device_hash: str
    ) -> Optional[Alert]:
        """
        Flag if a device is used by multiple accounts.
        This is a strong signal for account takeover or mule networks.
        """
        linked_accounts = self.graph.get_device_accounts(device_hash)

        if len(linked_accounts) >= self.settings.shared_device_threshold:
            # Don't create duplicate alerts for the same device
            existing = await self._alert_exists(
                db, "shared_device", device_hash
            )
            if existing:
                return None

            other_accounts = [a for a in linked_accounts if a != account_hash]
            risk_score = min(0.3 + 0.15 * len(other_accounts), 1.0)
            severity = self._score_to_severity(risk_score)

            alert = Alert(
                alert_type="shared_device",
                severity=severity,
                risk_score=round(risk_score, 2),
                account_id=account_hash,
                description=(
                    f"Device dev_{device_hash[:8]} is shared across "
                    f"{len(linked_accounts)} accounts. "
                    f"This may indicate a mule network or account takeover."
                ),
                details=json.dumps({
                    "device_id": device_hash,
                    "linked_accounts": linked_accounts,
                    "account_count": len(linked_accounts),
                }),
                related_nodes=json.dumps([device_hash] + linked_accounts),
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
            return alert

        return None

    async def _check_velocity(
        self, db: AsyncSession, account_hash: str
    ) -> Optional[Alert]:
        """
        Flag if an account has too many transactions in a short window.
        """
        txns = self.graph.get_account_transactions(account_hash)
        if len(txns) < self.settings.velocity_threshold:
            return None

        # Check timestamps within the window
        now = datetime.now(timezone.utc)
        recent_count = 0
        total_amount = 0.0

        for txn in txns:
            ts_str = txn.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                diff = (now - ts).total_seconds()
                if diff <= self.settings.velocity_window_seconds:
                    recent_count += 1
                    total_amount += txn.get("amount", 0)
            except (ValueError, TypeError):
                recent_count += 1  # Count if timestamp parsing fails

        if recent_count >= self.settings.velocity_threshold:
            existing = await self._alert_exists(db, "velocity", account_hash)
            if existing:
                return None

            risk_score = min(0.4 + 0.05 * recent_count, 1.0)
            severity = self._score_to_severity(risk_score)

            alert = Alert(
                alert_type="velocity",
                severity=severity,
                risk_score=round(risk_score, 2),
                account_id=account_hash,
                description=(
                    f"Account acct_{account_hash[:8]} made {recent_count} transactions "
                    f"totaling {total_amount:.2f} within the last "
                    f"{self.settings.velocity_window_seconds // 60} minutes. "
                    f"High transaction velocity detected."
                ),
                details=json.dumps({
                    "transaction_count": recent_count,
                    "total_amount": total_amount,
                    "window_seconds": self.settings.velocity_window_seconds,
                }),
                related_nodes=json.dumps([account_hash]),
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
            return alert

        return None

    async def _check_fan_out(
        self, db: AsyncSession, account_hash: str
    ) -> Optional[Alert]:
        """
        Flag if an account transacts at too many distinct merchants.
        Structuring pattern — spreading transactions to stay under limits.
        """
        merchants = self.graph.get_account_merchants(account_hash)

        if len(merchants) >= self.settings.fan_out_threshold:
            existing = await self._alert_exists(db, "fan_out", account_hash)
            if existing:
                return None

            risk_score = min(0.35 + 0.1 * len(merchants), 1.0)
            severity = self._score_to_severity(risk_score)

            alert = Alert(
                alert_type="fan_out",
                severity=severity,
                risk_score=round(risk_score, 2),
                account_id=account_hash,
                description=(
                    f"Account acct_{account_hash[:8]} transacted at "
                    f"{len(merchants)} different merchants. "
                    f"Possible structuring or card testing pattern."
                ),
                details=json.dumps({
                    "merchant_count": len(merchants),
                    "merchants": [m[:12] for m in merchants],
                }),
                related_nodes=json.dumps([account_hash] + merchants),
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
            return alert

        return None

    async def _check_cycles(
        self, db: AsyncSession, account_hash: str
    ) -> list[Alert]:
        """
        Detect circular money flow patterns (A→B→C→A layering).
        """
        alerts = []
        cycles = self.graph.find_cycles(max_length=6)

        for cycle in cycles:
            # Only create alerts for cycles involving this account
            if account_hash not in cycle:
                continue

            cycle_key = "_".join(sorted(cycle))
            existing = await self._alert_exists(db, "cycle", cycle_key)
            if existing:
                continue

            risk_score = min(0.6 + 0.1 * len(cycle), 1.0)
            severity = self._score_to_severity(risk_score)

            cycle_labels = [f"acct_{n[:8]}" if self.graph.graph.nodes.get(n, {}).get("node_type") == "account" else n[:8] for n in cycle]

            alert = Alert(
                alert_type="cycle",
                severity=severity,
                risk_score=round(risk_score, 2),
                account_id=account_hash,
                description=(
                    f"Circular transaction pattern detected: "
                    f"{' → '.join(cycle_labels)} → {cycle_labels[0]}. "
                    f"This is a classic money layering pattern."
                ),
                details=json.dumps({
                    "cycle_nodes": cycle,
                    "cycle_length": len(cycle),
                }),
                related_nodes=json.dumps(cycle),
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)
            alerts.append(alert)

        return alerts

    async def _alert_exists(self, db: AsyncSession, alert_type: str, key: str) -> bool:
        """Check if a similar alert already exists (deduplication)."""
        from sqlalchemy import select, and_

        query = select(Alert).where(
            and_(
                Alert.alert_type == alert_type,
                Alert.details.contains(key[:16]),
                Alert.status == "open",
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _score_to_severity(score: float) -> str:
        """Convert risk score to severity label."""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        return "low"
