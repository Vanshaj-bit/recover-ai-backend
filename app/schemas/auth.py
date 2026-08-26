from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

# Validates the incoming JSON when a merchant signs up
class MerchantCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters")
    business_name: str = Field(min_length=2, max_length=100)

# Formats the outgoing JSON so we never accidentally leak the password hash
class MerchantResponse(BaseModel):
    id: UUID
    email: str
    business_name: str
    is_active: bool

    class Config:
        from_attributes = True  # Allows Pydantic to read directly from SQLAlchemy models

# Defines the standard OAuth2 token response format
class Token(BaseModel):
    access_token: str
    token_type: str