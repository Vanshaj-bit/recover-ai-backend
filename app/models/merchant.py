import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class Merchant(Base):
    __tablename__ = "merchants"

    # Using UUIDs prevents attackers from guessing how many merchants we have
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    business_name = Column(String(255), nullable=False)
    
    # Soft-delete flag (better than deleting financial records entirely)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit timestamps automatically managed by PostgreSQL
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)