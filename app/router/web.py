from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Path
from starlette.requests import Request

from app.database import AsyncSession
from utils.jinja2_templates import Template
from utils.timing_decorator import RecordTiming

web_router = APIRouter()


@web_router.get("/")
async def web_index(template: Template, session: AsyncSession, timing: RecordTiming):
    timing("start")
    x = await session.execute(sa.text("SELECT 1"))
    timing("sql")
    response = await template("index.html")
    timing("response")
    return response


@web_router.get("/page/{page}")
async def web_page(template: Template, page: Annotated[int, Path(..., title="Page")]):
    return await template("index.html", page=page)


@web_router.get("/hello/{name}")
async def web_hello(template: Template, name: Annotated[str, Path(..., title="Name")]):
    return await template("hello.html", name=name)
