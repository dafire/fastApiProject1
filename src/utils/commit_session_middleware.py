from loguru import logger
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class CommitDatabaseSessionMiddleware:  # pylint: disable=too-few-public-methods
    """
    Middleware class that commits the database session after each HTTP response.

    Args:
        app (ASGIApp): The ASGI application to wrap.

    Attributes:
        app (ASGIApp): The wrapped ASGI application.

    """

    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":  # pragma: no cover
            await self.app(scope, receive, send)
            return

        async def _inner(message: Message) -> None:
            if message["type"] != "http.response.start":
                await send(message)
                return
            if "state" in scope and (session := scope["state"].get("sqlalchemy_session")):
                if session.is_active:
                    logger.info("Committing session")
                    await session.commit()
            await send(message)

        await self.app(scope, receive, _inner)
