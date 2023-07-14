from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from starlette.staticfiles import StaticFiles

import settings
from router.alembic import router
from router.web import web_router
from utils.jinja2_templates import JinjaTemplates
from utils.loguru_logger import replace_log_handlers
from utils.timing_middleware import add_timing_middleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Initialize Templates
    JinjaTemplates.initialize(
        template_path=settings.TEMPLATE_PATH,
        static_path=settings.STATIC_PATH,
        auto_reload=settings.DEBUG,
    )
    # Start Application
    yield


replace_log_handlers()

app = FastAPI(debug=settings.DEBUG, lifespan=lifespan)

if settings.DEBUG:
    add_timing_middleware(app, record=logger.opt(depth=3).debug, prefix="", exclude="StaticFiles")

app.include_router(web_router)
app.include_router(router, prefix="/alembic")

app.mount("/static", StaticFiles(directory=settings.STATIC_PATH), name="static")
