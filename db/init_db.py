import asyncio
from .database import engine
from models.base import Base
from sqlalchemy.ext.asyncio import async_sessionmaker

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def setup_database():
    print("Connecting to PostgreSQL to check/create tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database setup complete!")

if __name__ == "__main__":
    asyncio.run(setup_database())
