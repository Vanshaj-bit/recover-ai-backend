from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
import razorpay
from typing import List

from app.core.database import get_db
from app.core.config import settings
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.payment import Payment
from app.schemas.payment import PaymentOrderCreate, PaymentResponse
from app.tasks.recovery import send_payment_recovery_email

# Phase 2 Import: The Gemini AI Agent
from app.services.ai_agent import analyze_payment_failure

router = APIRouter()

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@router.post("/orders", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_order(
    order_in: PaymentOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """Create a Razorpay order and track it in our database."""
    # 1. Verify customer belongs to this merchant
    cust_query = select(Customer).where(
        Customer.id == order_in.customer_id,
        Customer.merchant_id == current_merchant.id
    )
    cust_result = await db.execute(cust_query)
    customer = cust_result.scalars().first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found or does not belong to your business.")

    # 2. Call Razorpay API to create an order
    try:
        rzp_order_data = {
            "amount": order_in.amount,
            "currency": order_in.currency,
            "payment_capture": 1 # Auto-capture payment
        }
        rzp_order = razorpay_client.order.create(data=rzp_order_data)
    except Exception as e:
        import uuid
        rzp_order = {"id": f"order_mock_{uuid.uuid4().hex[:10]}"}
        
    # 3. Save pending payment record in PostgreSQL
    new_payment = Payment(
        merchant_id=current_merchant.id,
        customer_id=customer.id,
        razorpay_order_id=rzp_order["id"],
        amount=order_in.amount,
        currency=order_in.currency,
        status="PENDING",
        metadata_obj=order_in.notes or {}
    )
    
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    
    return new_payment


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """List all payments for the logged-in merchant (Tenant Isolated)."""
    query = select(Payment).where(Payment.merchant_id == current_merchant.id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Listens for Razorpay events and triggers the AI Agent on failures."""
    payload = await request.json()
    event = payload.get("event")
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    order_id = payment_entity.get("order_id")
    
    if order_id:
        query = select(Payment).where(Payment.razorpay_order_id == order_id)
        result = await db.execute(query)
        payment_record = result.scalars().first()
        
        if payment_record:
            if event == "payment.captured":
                payment_record.status = "CAPTURED"
                payment_record.razorpay_payment_id = payment_entity.get("id")
                payment_record.payment_method = payment_entity.get("method")
                
            elif event == "payment.failed":
                payment_record.status = "FAILED"
                payment_record.razorpay_payment_id = payment_entity.get("id")
                payment_record.payment_method = payment_entity.get("method")
                payment_record.failure_code = payment_entity.get("error_code")
                payment_record.failure_reason = payment_entity.get("error_description")
                
                # --- PHASE 2: TRIGGER AI AGENT ---
                cust_query = select(Customer).where(Customer.id == payment_record.customer_id)
                cust_result = await db.execute(cust_query)
                customer = cust_result.scalars().first()
                customer_name = customer.name if customer else "Customer"
                
                ai_decision = await analyze_payment_failure(
                    customer_name=customer_name,
                    amount=payment_record.amount,
                    failure_reason=payment_record.failure_reason,
                    method=payment_record.payment_method or "unknown"
                )
                
                payment_record.metadata_obj = ai_decision
            
            await db.commit()
            
    return {"status": "success"}


@router.get("/force-patch")
async def force_patch_db(db: AsyncSession = Depends(get_db)):
    """Forcefully adds only the missing failure columns."""
    await db.execute(text("ALTER TABLE payments ADD COLUMN failure_code VARCHAR;"))
    await db.execute(text("ALTER TABLE payments ADD COLUMN failure_reason VARCHAR;"))
    await db.commit()
    return {"message": "Forced patch successful! Columns added."}


@router.post("/recover/{payment_id}")
async def trigger_recovery_link(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """Programmatically generate a Razorpay Payment Link for a failed transaction."""
    query = select(Payment).where(
        Payment.id == payment_id,
        Payment.merchant_id == current_merchant.id
    )
    result = await db.execute(query)
    payment = result.scalars().first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found.")

    cust_query = select(Customer).where(Customer.id == payment.customer_id)
    cust_result = await db.execute(cust_query)
    customer = cust_result.scalars().first()

    try:
        link_payload = {
            "amount": payment.amount,
            "currency": payment.currency or "INR",
            "accept_partial": False,
            "description": f"Complete your failed payment for order #{payment.razorpay_order_id}",
            "customer": {
                "name": customer.name if customer else "Valued Customer",
                "email": customer.email if customer else "customer@example.com",
                "contact": customer.phone if customer and customer.phone else "9999999999"
            },
            "notify": {
                "sms": True,
                "email": True
            },
            "reminder_enable": True,
            "callback_url": "https://recover-ai-frontend.vercel.app/dashboard",
            "callback_method": "get"
        }

        response = razorpay_client.payment_link.create(link_payload)
        
        return {
            "status": "success",
            "payment_link_id": response.get("id"),
            "short_url": response.get("short_url"),
            "message": "Recovery link generated and dispatched successfully!"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))