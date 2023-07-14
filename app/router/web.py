from typing import Annotated

from fastapi import APIRouter, Path

from utils.jinja2_templates import Template
from app.database import AsyncSession
import sqlalchemy as sa
web_router = APIRouter()


@web_router.get("/")
async def web_index(template: Template, session: AsyncSession):
    x = await session.execute(sa.text("SELECT 1"))
    print(x)
    return template("index.html")


@web_router.get("/page/{page}")
async def web_page(template: Template, page: Annotated[int, Path(..., title="Page")]):
    return template("index.html", page=page)


@web_router.get("/hello/{name}")
async def web_hello(template: Template, name: Annotated[str, Path(..., title="Name")]):
    return template("hello.html", name=name)
