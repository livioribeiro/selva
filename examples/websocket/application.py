import logging
from pathlib import Path

from starlette.websockets import WebSocketDisconnect

from asgikit.requests import Request
from asgikit.websockets import WebSocket

from selva.configuration import Settings
from selva.di import Inject, service
from selva.web import controller, get, websocket
from selva.web.exception import WebSocketException

logger = logging.getLogger(__name__)


@service
class WebSocketService:
    def __init__(self):
        self.clients: dict[str, WebSocket] = {}

    async def handle_websocket(self, request: Request):
        ws = request.websocket
        client = str(ws.client)
        self.clients[client] = ws

        while True:
            try:
                message = await ws.receive()
                logger.info(
                    "client message: content=%s, client=%s", message, repr(client)
                )
                await self.broadcast(message)
            except (WebSocketDisconnect, WebSocketException):
                logger.info("client disconnected: %s", repr(client))
                del self.clients[client]
                break

    async def broadcast(self, message: str):
        if message.lower() == "ping":
            message = "Pong"

        for ws in self.clients.values():
            try:
                await ws.send(message)
            except (WebSocketDisconnect, WebSocketException):
                logger.info("client disconnected: %s", repr(ws.client))


@controller
class WebSocketController:
    handler: WebSocketService = Inject()
    settings: Settings = Inject()
    index_html = (Path() / "resources" / "static" / "index.html").absolute()

    @get
    def index(self):
        return FileResponse(self.index_html)

    @websocket("/chat")
    async def chat(self, context: RequestContext):
        ws = context.websocket

        await ws.accept()
        logger.info("client connected: %s", repr(ws.client))

        await self.handler.handle_websocket(ws)
