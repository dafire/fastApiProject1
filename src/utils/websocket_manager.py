from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from loguru import logger
from starlette.websockets import WebSocket, WebSocketDisconnect


@dataclass
class WebsocketConnection:
    user: UUID
    session: str


class WebsocketManager:
    active_connections: dict[WebSocket:WebsocketConnection] = {}

    async def register_socket(self, websocket: WebSocket):
        logger.warning("connect {}", websocket.cookies)
        session = websocket.cookies.get("session")
        # TODO: validate session and user
        await websocket.accept()
        self.active_connections[websocket] = WebsocketConnection(
            user=UUID("00000000-0000-0000-0000-000000000000"), session=session
        )
        await websocket.send_json(dict(some="nessage"))
        try:
            while True:
                data = await websocket.receive_json()
                logger.debug("incoming websocket data {}", data)
        except WebSocketDisconnect:
            logger.warning("disconnected {}", websocket)
            del self.active_connections[websocket]


WebsocketManagerDependency = Annotated[WebsocketManager, Depends(WebsocketManager)]
