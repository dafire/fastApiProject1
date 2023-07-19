import typing
import uuid

import orjson
from loguru import logger
from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from db.dependencies import Redis
from db.models import User


class SessionDict(dict):
    _value_changed = False
    _redis: Redis = None

    async def load(self, session_id: str):
        if not self._redis:
            raise RuntimeError("Redis is not initialized")
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

    async def save(self, session_id, *, duration=3600, force=False):
        if not self._redis:
            raise RuntimeError("Redis is not initialized")
        if force or self._value_changed:
            await self._redis.setex(session_id, duration, orjson.dumps(self))
            return True
        return False

    async def delete(self, session_id):
        if not self._redis:
            raise RuntimeError("Redis is not initialized")
        await self._redis.delete(session_id)

    @classmethod
    async def initialize(cls, redis: Redis):
        cls._redis = redis


class SessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        secret_key: typing.Union[str, Secret],
        session_cookie: str = "session",
        max_age: typing.Optional[int] = 14 * 24 * 60 * 60,
        path: str = "/",
        same_site: typing.Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
    ):
        self.app = app
        self.secret_key = secret_key
        self.path = path
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.security_flags = "httponly; samesite=" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        session_id = uuid.uuid4().hex
        connection = HTTPConnection(scope)
        initial_session_was_empty = True

        scope["user"] = None
        scope["session"] = SessionDict()
        if self.session_cookie in connection.cookies and (cookie := connection.cookies[self.session_cookie].encode("utf-8")):
            if len(cookie) == 32:
                session_id = cookie.decode("utf-8")
                if await scope["session"].load(session_id):
                    logger.info("Session loaded from redis [{}] {}", session_id, scope["session"])
                    initial_session_was_empty = False
                    if user_data := scope["session"].get("user"):
                        scope["user"] = User(**user_data)
                else:
                    logger.warning("Session not found in redis {}", session_id)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                if scope["session"]:
                    # We have session data to persist.
                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(
                        session_cookie=self.session_cookie,
                        data=session_id,
                        path=self.path,
                        max_age=f"Max-Age={self.max_age}; " if self.max_age else "",
                        security_flags=self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
                    saved = await scope["session"].save(session_id, duration=self.max_age, force=True)
                elif not initial_session_was_empty:
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(  # noqa E501
                        session_cookie=self.session_cookie,
                        data="null",
                        path=self.path,
                        expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                        security_flags=self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
                    await scope["session"].delete(session_id)
                    logger.info("Session [{}] deleted", session_id)
            await send(message)

        await self.app(scope, receive, send_wrapper)
