import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import Base
# Import your models so Base knows about them
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.payment import Payment

# Use your exact Supabase pooler connection string with the raw exclamation mark!
DATABASE_URL = "postgresql+asyncpg://postgres.xsszqhzvgsonekgesvit:Sharpner3012!@aws-0-ap-southeast-2.pooler.supabase.com:6543/postgres"

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