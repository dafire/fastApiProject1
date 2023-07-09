import os

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import settings
from router.alembic import router
from router.web import web_router
from utils.jinja2_templates import JinjaTemplates
from utils.loguru_logger import replace_log_handlers

app = FastAPI(debug=settings.DEBUG)

replace_log_handlers()

app.include_router(web_router)
app.include_router(router, prefix="/alembic")

static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))

app.mount("/static", StaticFiles(directory=static_folder), name="static")

JinjaTemplates.initialize(template_path=template_folder, static_path=static_folder, auto_reload=settings.DEBUG)


@app.get("/h/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}"}
