import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base

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

# PUBLIC_INTERFACE
def get_base():
    """
    Returns the SQLAlchemy declarative base containing all ORM models (including ApprovalWorkflowInstanceStepApprover).
    This can be used for migration script autogeneration or metadata access.
    """
    return Base

# PUBLIC_INTERFACE
async def init_db():
    """
    Create all tables in the database based on registered ORM models (including new Approver assignment table).
    Should be run only during setup or migrations.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
