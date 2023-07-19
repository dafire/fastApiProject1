from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.redis import get_redis_connection
from utils.jinja2_templates import JinjaTemplates
from utils.session_middleware import SessionDict


@asynccontextmanager
async def lifespan(_: FastAPI):
    await SessionDict.initialize(redis=await get_redis_connection())
    # Initialize Templates
    JinjaTemplates.initialize()
    # Start Application
    yield
