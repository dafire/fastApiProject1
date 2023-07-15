import uuid
from typing import Callable

import orjson
from fastapi.routing import APIRoute
from loguru import logger
from starlette.requests import Request
from starlette.responses import Response

from db.dependencies import Redis
from db.redis import get_redis_connection


class SessionDict:
    _value_changed = False

    def __init__(self, redis: Redis):
        self._redis = redis
        self._data = {}

    async def load(self, session_id: str):
        if session_id:
            data = await self._redis.get(session_id)
            if data:
                self._data = orjson.loads(data)
                return True
        return False

    def __setitem__(self, item, value):
        self._value_changed = True
        self._data[item] = value

    def __getitem__(self, item):
        return self._data[item]

    def get(self, item, default=None):
        return self._data.get(item, default)

    async def save(self, session_id):
        if self._value_changed:
            await self._redis.setex(session_id, 3600, orjson.dumps(self._data))
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
                if not await request.scope["session"].load(session_id):
                    delete_session = True
                    new_session = True
                    session_id = str(uuid.uuid4())
            else:
                new_session = True
                session_id = str(uuid.uuid4())

            response = await original_route_handler(request)

            if await request.scope["session"].save(session_id):
                if new_session:
                    logger.debug("Set Session Cookie")
                    response.set_cookie("session_id", httponly=True, value=session_id)
            elif delete_session:
                logger.debug("Delete Session Cookie")
                response.delete_cookie("session_id")

            return response

        return custom_route_handler
