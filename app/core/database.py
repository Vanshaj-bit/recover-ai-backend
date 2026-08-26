from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create the async engine connected to our Docker Postgres container
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for our models
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session