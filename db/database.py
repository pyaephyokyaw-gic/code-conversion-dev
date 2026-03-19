from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import DATABASE_URL


if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Set to False in production
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

# Dependency for FastAPI


async def get_db() -> AsyncSession:
    """
    Provide a session for FastAPI routes using `Depends(get_db)`
    """
    async with AsyncSessionLocal() as session:
        yield session
