from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Path
from starlette.requests import Request

from db.dependencies import AsyncSession
from utils.jinja2_templates import Template
from utils.session_route import SessionRoute
from utils.timing_decorator import RecordTiming

web_router = APIRouter(route_class=SessionRoute)


@web_router.get("/")
async def web_index(template: Template, session: AsyncSession, timing: RecordTiming, request: Request):
    timing("start")
    x = (await session.execute(sa.text("SELECT 1"))).scalar_one()
    timing("sql")
    test = request.session.get("test", 0)
    test += 1
    request.session["test"] = test
    return await template("index.html", test=test)


@web_router.get("/page/{page}")
async def web_page(template: Template, request: Request, page: Annotated[int, Path(..., title="Page")]):
    test = request.session.get("test", 0)
    return await template("index.html", page=page, test=test)


@web_router.get("/hello/{name}")
async def web_hello(template: Template, name: Annotated[str, Path(..., title="Name")]):
    return await template("hello.html", name=name)
