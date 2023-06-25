import os

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import settings
from utils.jinja2_templates import JinjaTemplates
from router.web import web_router
from router.alembic import router
from utils.loguru_logger import replace_log_handlers

app = FastAPI(debug=settings.DEBUG)

replace_log_handlers()

app.include_router(web_router)
app.include_router(router, prefix="/alembic")
app.mount("/static", StaticFiles(directory="static"), name="static")

template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
JinjaTemplates.initialize(template_folder, auto_reload=settings.DEBUG)


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
