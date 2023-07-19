from fastapi import FastAPI
from loguru import logger
from rich.pretty import pprint
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from lifespan import lifespan
from router import login_router
from router.alembic import router
from router.web import web_router
from settings import Settings, get_settings
from utils.commit_session_middleware import CommitDatabaseSessionMiddleware
from utils.loguru_logger import replace_log_handlers
from utils.session_middleware import SessionMiddleware
from utils.timing_middleware import add_timing_middleware


def create_web_app():
    settings = get_settings(Settings)

    replace_log_handlers()

    middlewares = [
        Middleware(SessionMiddleware, secret_key=settings.secret_key, path="/", session_cookie="session_id"),
        Middleware(CommitDatabaseSessionMiddleware),
    ]

    app = FastAPI(debug=settings.debug, lifespan=lifespan, middleware=middlewares)

    logger.info("Debug mode: {}", settings.debug)

    if settings.debug:
        add_timing_middleware(app, record=logger.opt(depth=3).debug, prefix="", exclude="StaticFiles")

    app.include_router(router)
    app.include_router(web_router)
    app.include_router(login_router)
    app.mount("/static", StaticFiles(directory=settings.static_folder), name="static")

    @app.get("/test")
    def test(request: Request):
        pprint(request.session)
        value = request.session.get("test", 0)
        request.session["test"] = value + 1
        return {"status": "ok", "value": value}

    return app
