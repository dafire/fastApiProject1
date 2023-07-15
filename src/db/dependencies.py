import contextlib
from collections.abc import AsyncIterator
from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession

from .engine import async_session_factory
from .redis import get_redis_connection


async def get_session(request: Request) -> AsyncIterator[_AsyncSession]:
    async with async_session_factory() as session:
        request.state.sqlalchemy_session = session
        yield session


@contextlib.asynccontextmanager
async def create_session() -> AsyncIterator[_AsyncSession]:
    async with async_session_factory() as session:
        yield session


AsyncSession = Annotated[_AsyncSession, Depends(get_session)]

Redis = Annotated[redis.Redis, Depends(get_redis_connection)]
