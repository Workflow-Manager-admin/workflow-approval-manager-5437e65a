import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (
    f'postgresql+asyncpg://{os.environ.get("POSTGRES_USER")}:'
    f'{os.environ.get("POSTGRES_PASSWORD")}@'
    f'{os.environ.get("POSTGRES_URL", "localhost")}:'
    f'{os.environ.get("POSTGRES_PORT","5432")}/'
    f'{os.environ.get("POSTGRES_DB")}'
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# PUBLIC_INTERFACE
async def get_db():
    """Yields a database session for FastAPI dependency injection."""
    async with AsyncSessionLocal() as session:
        yield session
