import os
from functools import cache
from pathlib import Path
import orjson

from fastapi import FastAPI
from jinja2 import pass_context
from rich.pretty import pprint
from starlette.staticfiles import StaticFiles

import settings
from utils.jinja2_templates import JinjaTemplates, Template
from router.web import web_router
from router.alembic import router
from utils.loguru_logger import replace_log_handlers

app = FastAPI(debug=settings.DEBUG)

replace_log_handlers()

app.include_router(web_router)
app.include_router(router, prefix="/alembic")
app.mount("/static", StaticFiles(directory="static"), name="static")

template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
jinja2env = JinjaTemplates.initialize(template_folder, auto_reload=settings.DEBUG)


##
@pass_context  # context is required otherwise jinja2 caches the result in bytecode for constants
def debug_asset_filter(_, path):
    txt = Path(os.path.join("static", "assets-manifest.json")).read_text()
    return orjson.loads(txt).get(path)


@cache  # jinja caches that if input is a constant, but to be sure we cache it here too
def asset_filter(path):
    return debug_asset_filter(None, path)


if settings.DEBUG:
    jinja2env.filters["asset"] = debug_asset_filter
else:
    jinja2env.filters["asset"] = asset_filter


@app.get("/h/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {asset_filter.__wrapped__(name)}"}
