from sqlalchemy import Column, String, Float, DateTime
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    tx_id = Column(String, primary_key=True)
    account_hash = Column(String, index=True)
    merchant_hash = Column(String, index=True)
    device_hash = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String)
    channel = Column(String)
    merchant_category = Column(String)
    timestamp = Column(String)  # ISO format string
