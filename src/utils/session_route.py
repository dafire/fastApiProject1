import uuid
from typing import Callable

import orjson
from fastapi import HTTPException
from fastapi.routing import APIRoute
from loguru import logger
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from db.dependencies import Redis
from db.models import User
from db.redis import get_redis_connection


class SessionDict(dict):
    _value_changed = False

    def __init__(self, redis: Redis):
        self._redis = redis
        super().__init__()

    async def load(self, session_id: str):
        if session_id:
            data = await self._redis.get(session_id)
            if data:
                self.update(orjson.loads(data))
                return True
        return False

    def __setitem__(self, item, value):
        self._value_changed = True
        return super().__setitem__(item, value)

    def __getitem__(self, item):
        return super().__getitem__(item)

    def __delitem__(self, key):
        self._value_changed = True
        return super().__delitem__(key)

    def get(self, item, default=None):
        return super().get(item, default)

    def pop(self, item, default=None):
        self._value_changed = True
        return super().pop(item, default)

    def clear(self):
        self._value_changed = True
        return super().clear()

    async def save(self, session_id):
        if self._value_changed:
            await self._redis.setex(session_id, 3600, orjson.dumps(self))
            return True
        return False


class SessionRoute(APIRoute):
    redis: Redis = None

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request.scope["user"] = None

            if not self.redis:
                self.redis = await get_redis_connection()

            request.scope["session"] = SessionDict(self.redis)
            session_id = request.cookies.get("session_id")
            delete_session = False
            new_session = False

            if session_id:
                if await request.scope["session"].load(session_id):
                    if user_data := request.scope["session"].get("user"):
                        request.scope["user"] = User(**user_data)
                else:
                    delete_session = True
                    new_session = True
                    session_id = str(uuid.uuid4())
            else:
                new_session = True
                session_id = str(uuid.uuid4())

            try:
                response = await original_route_handler(request)
            except HTTPException as e:
                if e.status_code == status.HTTP_401_UNAUTHORIZED:
                    request.scope["session"]["login_redirect"] = f"{request.url.path}?{request.url.query}"
                    response = RedirectResponse(request.url_for("login"), status_code=status.HTTP_303_SEE_OTHER)
                else:
                    raise e

            if await request.scope["session"].save(session_id):
                if new_session:
                    logger.debug("Set Session Cookie")
                    response.set_cookie("session_id", httponly=True, value=session_id)
            elif delete_session:
                logger.debug("Delete Session Cookie")
                response.delete_cookie("session_id")

            return response

        return custom_route_handler
