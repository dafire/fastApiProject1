from fastapi import FastAPI
from loguru import logger
from starlette.staticfiles import StaticFiles

from lifespan import lifespan
from router import login_router
from router.alembic import router
from router.web import web_router
from settings import Settings, get_settings
from utils.commit_session_middleware import CommitSessionMiddleware
from utils.loguru_logger import replace_log_handlers
from utils.timing_middleware import add_timing_middleware


def create_web_app():
    settings = get_settings(Settings)

    replace_log_handlers()

    app = FastAPI(debug=settings.debug, lifespan=lifespan)

    app.add_middleware(CommitSessionMiddleware)

    if settings.debug:
        add_timing_middleware(app, record=logger.opt(depth=3).debug, prefix="", exclude="StaticFiles")

    app.include_router(router)
    app.include_router(web_router)
    app.include_router(login_router)
    app.mount("/static", StaticFiles(directory=settings.static_folder), name="static")

    return app
