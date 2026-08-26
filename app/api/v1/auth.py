from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_merchant
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.merchant import Merchant
from app.schemas.auth import MerchantCreate, MerchantResponse, Token

router = APIRouter()

@router.post("/signup", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
async def signup(merchant_in: MerchantCreate, db: AsyncSession = Depends(get_db)):
    """Register a new merchant account."""
    # 1. Check if user already exists
    query = select(Merchant).where(Merchant.email == merchant_in.email)
    result = await db.execute(query)
    existing_merchant = result.scalars().first()
    
    if existing_merchant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A merchant with this email already exists."
        )
    
    # 2. Hash the password and create the user
    hashed_pw = get_password_hash(merchant_in.password)
    new_merchant = Merchant(
        email=merchant_in.email,
        password_hash=hashed_pw,
        business_name=merchant_in.business_name
    )
    
    # 3. Save to database
    db.add(new_merchant)
    await db.commit()
    await db.refresh(new_merchant)
    
    return new_merchant


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Authenticate a merchant and return a JWT."""
    # OAuth2 natively uses 'username', but we map it to our 'email' field
    query = select(Merchant).where(Merchant.email == form_data.username)
    result = await db.execute(query)
    merchant = result.scalars().first()
    
    # Check if merchant exists AND password is correct
    if not merchant or not verify_password(form_data.password, merchant.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate the JWT containing the merchant's UUID
    access_token = create_access_token(data={"sub": str(merchant.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.get("/me", response_model=MerchantResponse)
async def read_current_merchant(
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """Get the profile of the currently logged-in merchant."""
    return current_merchant