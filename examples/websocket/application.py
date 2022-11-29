from pathlib import Path

from starlette.exceptions import WebSocketException
from starlette.responses import FileResponse

from selva.configuration import Settings
from selva.di import Inject, service
from selva.logging import get_logger
from selva.web import RequestContext, WebSocket, controller, get, websocket

logger = get_logger()


@service
class WebSocketService:
    def __init__(self):
        self.clients: set[WebSocket] = set()

    async def handle_client(self, client: WebSocket):
        self.clients.add(client)
        while True:
            try:
                message = await client.receive_text()
                logger.info("client message", content=message, client=client.client)
                await self.broadcast(message)
            except WebSocketException:
                logger.info("client disconnected", client=client.client)
                self.clients.remove(client)
                break

    async def broadcast(self, message: str):
        if message.lower() == "ping":
            message = "Pong"

        for client in self.clients:
            try:
                await client.send_text(message)
            except WebSocketException:
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
