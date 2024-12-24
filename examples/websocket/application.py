from pathlib import Path
from typing import Annotated

from asgikit.errors.websocket import WebSocketDisconnectError
from asgikit.requests import Request
from asgikit.responses import respond_file
from asgikit.websockets import WebSocket
import structlog

from selva.configuration import Settings
from selva.di import Inject, service
from selva.web import controller, get, websocket
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
            message = "Pong"

        for client, ws in self.clients.items():
            try:
                await ws.send(message)
            except (WebSocketDisconnectError, WebSocketException):
                del self.clients[client]
                logger.info("client disconnected", client=repr(client))



index_html = (Path() / "resources" / "static" / "index.html").absolute()

@get
async def index(request: Request):
    await respond_file(request.response, index_html)

@websocket("/chat")
async def chat(
    request: Request,
    handler: Annotated[WebSocketService, Inject],
):
    await request.websocket.accept()
    await handler.handle_websocket(request)
