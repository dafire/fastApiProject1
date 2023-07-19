from typing import Annotated

from fastapi import APIRouter, Depends, Path
from starlette.requests import Request
from starlette.websockets import WebSocket

from db.dependencies import AsyncSession
from router.login import login_required
from utils.jinja2_templates import Template
from utils.timing_decorator import RecordTiming
from utils.websocket_manager import WebsocketManagerDependency

web_router = APIRouter(dependencies=[Depends(login_required)])


@web_router.get("/")
async def web_index(template: Template, session: AsyncSession, timing: RecordTiming, request: Request):
    timing("start")
    return await template("index.html")


@web_router.get("/page/{page}")
async def web_page(template: Template, request: Request, page: Annotated[int, Path(..., title="Page")]):
    test = request.session.get("test")
    return await template("index.html", page=page, test=test)


@web_router.get("/hello/{name}")
async def web_hello(template: Template, name: Annotated[str, Path(..., title="Name")]):
    return await template("hello.html", name=name)


@web_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, manager: WebsocketManagerDependency):
    await manager.register_socket(websocket)
