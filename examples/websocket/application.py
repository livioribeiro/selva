from pathlib import Path

from selva.di import service
from selva.web import (
    FileResponse,
    RequestContext,
    WebSocket,
    controller,
    get,
    websocket,
)
from selva.web.configuration import Settings
from selva.web.errors import WebSocketDisconnectError, WebSocketStateError


@service
class WebSocketService:
    def __init__(self):
        self.clients: set[WebSocket] = set()

    async def broadcast(self, message: str):
        if message.lower() == "ping":
            message = "Pong"

        disconnected = set()
        for client in self.clients:
            try:
                await client.send_text(message)
            except WebSocketStateError:
                disconnected.add(client)

        self.clients -= disconnected


@controller
class WebSocketController:
    def __init__(self, handler: WebSocketService, settings: Settings):
        self.handler = handler
        self.settings = settings

    @get
    def index(self):
        return FileResponse(self.settings.resource_path("static", "index.html"))

    @websocket("/chat")
    async def chat(self, context: RequestContext):
        client = context.websocket

        await client.accept()
        print("[open] Client connected")

        self.handler.clients.add(client)

        while True:
            try:
                message = await client.receive()
                print(f"[message] {message}")
                await self.handler.broadcast(message)
            except WebSocketDisconnectError:
                print("[close] Client disconnected")
                break
