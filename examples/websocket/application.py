from pathlib import Path

from selva.configuration import Settings
from selva.di import Inject, service
from selva.logging import get_logger
from selva.web import (
    FileResponse,
    RequestContext,
    WebSocket,
    controller,
    get,
    websocket,
)
from selva.web.errors import WebSocketDisconnectError, WebSocketStateError

logger = get_logger()


@service
class WebSocketService:
    def __init__(self):
        self.clients: set[WebSocket] = set()

    async def handle_client(self, client: WebSocket):
        self.clients.add(client)
        while True:
            try:
                message = await client.receive()
                logger.info("client message", content=message, client=client.client)
                await self.broadcast(message)
            except WebSocketDisconnectError:
                logger.info("client disconnected", client=client.client)
                self.clients.remove(client)
                break

    async def broadcast(self, message: str):
        if message.lower() == "ping":
            message = "Pong"

        for client in self.clients:
            try:
                await client.send_text(message)
            except WebSocketStateError:
                logger.info("client disconnected", client=client.client)


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
        client = context.websocket

        await client.accept()
        logger.info("client connected", client=client.client)

        await self.handler.handle_client(client)
