import time
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from loguru import logger
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession, async_sessionmaker, create_async_engine

from . import settings

__all__ = ["AsyncSession", "load_models"]

async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql:", "postgresql+asyncpg:"), pool_pre_ping=True, echo=settings.DEBUG and False
)

async_session_maker = async_sessionmaker(bind=async_engine, autoflush=False, future=True, expire_on_commit=False)

if settings.DEBUG:

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())
        # print("Start Query:\n" + str(statement) % parameters + "\n")

    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        logger.opt(depth=6).debug("{} [{:.5f}]", statement, total)

    event.listen(async_engine.sync_engine, "before_cursor_execute", before_cursor_execute)
    event.listen(async_engine.sync_engine, "after_cursor_execute", after_cursor_execute)


async def get_async_session() -> AsyncGenerator[_AsyncSession, None]:
    async with async_session_maker() as session:
        # event.listen(session.sync_session, "before_commit", my_before_commit)
        yield session


AsyncSession = Annotated[_AsyncSession, Depends(get_async_session)]


def load_models():
    """called from alembic to create migrations"""
    import os

    files = filter(
        lambda e: not e.startswith("__"),
        os.listdir(os.path.join(os.path.dirname(__file__), "models")),
    )
    for file in files:
        exec(f"from .models import {os.path.splitext(file)[0]}")
