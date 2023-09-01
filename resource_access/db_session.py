from core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

async_engine = create_async_engine(
    settings.postgres_async_url,
    pool_pre_ping=True,
    pool_size=settings.async_pool_size,
    pool_recycle=settings.async_pool_recycle,
    max_overflow=settings.async_max_overflow,
)
AsyncSessionLocal = sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)

sync_engine = create_engine(
    settings.postgres_url,
    pool_size=settings.sync_pool_size,
    pool_recycle=settings.sync_pool_recycle,
    max_overflow=settings.sync_max_overflow,
)
SessionLocal = sessionmaker(
    bind=sync_engine, expire_on_commit=False, class_=Session
)
