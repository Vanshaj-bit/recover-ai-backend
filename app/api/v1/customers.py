from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_merchant
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter()

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_in: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """Create a new customer scoped to the logged-in merchant."""
    # Check if customer with this email already exists for THIS merchant
    query = select(Customer).where(
        Customer.merchant_id == current_merchant.id,
        Customer.email == customer_in.email
    )
    result = await db.execute(query)
    existing_customer = result.scalars().first()
    
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A customer with this email already exists for your business."
        )
        
    new_customer = Customer(
        merchant_id=current_merchant.id,
        name=customer_in.name,
        email=customer_in.email,
        phone=customer_in.phone
    )
    
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    
    return new_customer


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """List all customers belonging to the logged-in merchant (Tenant Isolated)."""
    query = select(Customer).where(Customer.merchant_id == current_merchant.id).offset(skip).limit(limit)
    result = await db.execute(query)
    customers = result.scalars().all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """Get a specific customer by ID, ensuring it belongs to the logged-in merchant."""
    query = select(Customer).where(
        Customer.id == customer_id,
        Customer.merchant_id == current_merchant.id
    )
    result = await db.execute(query)
    customer = result.scalars().first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found."
        )
        
    return customer