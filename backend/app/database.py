import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Fallback to sqlite if postgres is not available
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./zsm_record.db"
)

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# For SQLite, we need connect_args={"check_same_thread": False}
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=False,
    connect_args=connect_args
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
