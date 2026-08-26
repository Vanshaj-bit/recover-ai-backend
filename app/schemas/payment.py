from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class PaymentOrderCreate(BaseModel):
    customer_id: UUID
    amount: int = Field(..., gt=0, description="Amount in smallest currency unit (e.g., paise)")
    currency: str = Field(default="INR")
    notes: Optional[Dict[str, Any]] = None

class PaymentResponse(BaseModel):
    id: UUID4
    merchant_id: UUID4
    customer_id: UUID4
    razorpay_order_id: str
    razorpay_payment_id: Optional[str] = None
    amount: int
    currency: str
    status: str
    payment_method: Optional[str] = None
    
    # --- PHASE 2 AI FIELDS ---
    failure_code: Optional[str] = None
    failure_reason: Optional[str] = None
    metadata_obj: Optional[Dict[str, Any]] = None 
    
    created_at: datetime

    class Config:
        from_attributes = True