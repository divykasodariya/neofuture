"""
Alert ORM model — stored in SQLite.
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), nullable=False)  # shared_device, velocity, cycle, fan_out
    severity = Column(String(20), nullable=False)     # critical, high, medium, low
    risk_score = Column(Float, nullable=False)         # 0.0 - 1.0
    account_id = Column(String(64), nullable=False)    # hashed account
    description = Column(Text, nullable=False)         # human-readable reason
    details = Column(Text, nullable=True)              # JSON blob with extra context
    related_nodes = Column(Text, nullable=True)        # JSON array of related node IDs
    status = Column(String(20), default="open")        # open, confirmed, false_positive, escalated
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
