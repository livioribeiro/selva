from typing import Annotated as A

import structlog
from asgikit.errors.websocket import WebSocketDisconnectError
from asgikit.requests import Request
from asgikit.websockets import WebSocket

from selva.di import Inject, service
from selva.web import websocket
from selva.web.exception import WebSocketException

logger = structlog.get_logger()


@service
class WebSocketService:
    def __init__(self):
        self.clients: dict[str, WebSocket] = {}

    async def handle_websocket(self, request: Request):
        client = str(request.client)
        ws = request.websocket
        self.clients[client] = ws

        logger.info("client connected", client=repr(client))

        while True:
            try:
                message = await ws.receive()
                logger.info("client message", content=message, client=repr(client))
                await self.broadcast(message)
            except (WebSocketDisconnectError, WebSocketException):
                logger.info("client disconnected", client=repr(client))
                del self.clients[client]
                break

    async def broadcast(self, message: str):
        if message.lower() == "ping":
            message = message.replace("i", "o").replace("I", "O")

        for client, ws in self.clients.items():
            try:
                await ws.send(message)
            except (WebSocketDisconnectError, WebSocketException):
                del self.clients[client]
                logger.info("client disconnected", client=repr(client))


@websocket("/chat")
async def chat(request: Request, handler: A[WebSocketService, Inject]):
    await request.websocket.accept()
    await handler.handle_websocket(request)
