from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from . import settings

__all__ = ["AsyncDBSession", "load_models"]

async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql:", "postgresql+asyncpg:"),
    pool_pre_ping=True,
    echo=settings.DEBUG and False,
)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    future=True,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


AsyncDBSession = Annotated[AsyncSession, Depends(get_async_session)]


def load_models():
    """called from alembic to create migrations"""
    import os

    files = filter(lambda e: not e.startswith("__"), os.listdir(os.path.join(os.path.dirname(__file__), "models")))
    for file in files:
        exec(f"from .models import {os.path.splitext(file)[0]}")
