from pathlib import Path

from selva.configuration import Settings
from selva.di import Inject, service
from selva.logging import get_logger
from selva.web import RequestContext, WebSocket, controller, get, websocket
from selva.web.errors import WebSocketException
from selva.web.responses import FileResponse

logger = get_logger()


@service
class WebSocketService:
    def __init__(self):
        self.clients: dict[str, WebSocket] = {}

    async def handle_websocket(self, ws: WebSocket):
        client = str(ws.client)
        self.clients[client] = ws

        while True:
            try:
                message = await ws.receive_text()
                logger.info("client message", content=message, client=ws.client)
                await self.broadcast(message)
            except WebSocketException:
                logger.info("client disconnected", client=ws.client)
                del self.clients[client]
                break

    async def broadcast(self, message: str):
        if message.lower() == "ping":
            message = "Pong"

        for ws in self.clients.values():
            try:
                await ws.send_text(message)
            except WebSocketException:
                logger.info("client disconnected", client=ws.client)


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
        logger.info("client connected", client=ws.client)

        await self.handler.handle_websocket(ws)
