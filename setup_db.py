import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import Base
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.payment import Payment

# Use the direct connection string with SSL parameters for asyncpg so it bypasses pooler tenant lookup issues
DATABASE_URL = "postgresql+asyncpg://postgres:Sharpner3012!@db.xsszqhzvgsonekgesvit.supabase.co:5432/postgres?ssl=require"

async def init_db():
    print("Connecting to Supabase...")
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        print("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())