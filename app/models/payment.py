import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False, index=True)
    # ON DELETE RESTRICT: We never want to accidentally delete a financial record if a customer is deleted
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    
    # Razorpay Specific Identifiers
    razorpay_order_id = Column(String(100), unique=True, nullable=False, index=True)
    razorpay_payment_id = Column(String(100), unique=True, nullable=True, index=True)
    
    # Financials (Stored in smallest currency unit, e.g., paise)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    
    # PENDING, AUTHORIZED, CAPTURED, FAILED, REFUNDED
    status = Column(String(30), nullable=False, index=True)
    payment_method = Column(String(50), nullable=True) 
    failure_code = Column(String, nullable=True)
    failure_reason = Column(String, nullable=True)
    
    # A place to store extra data without changing the schema
    metadata_obj = Column(JSONB, server_default='{}', nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)