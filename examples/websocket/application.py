from selva.di import service, Inject
from selva.web import (
    FileResponse,
    RequestContext,
    WebSocket,
    controller,
    get,
    websocket,
)
from selva.configuration import Settings
from selva.web.errors import WebSocketDisconnectError, WebSocketStateError


@service
class WebSocketService:
    def __init__(self):
        self.clients: set[WebSocket] = set()

    async def handle_client(self, client: WebSocket):
        self.clients.add(client)
        while True:
            try:
                message = await client.receive()
                print(f"[message] {message}")
                await self.broadcast(message)
            except WebSocketDisconnectError:
                print("[close] Client disconnected")
                self.clients.remove(client)
                break

    async def broadcast(self, message: str):
        if message.lower() == "ping":
            message = "Pong"

        for client in self.clients:
            try:
                await client.send_text(message)
            except WebSocketStateError:
                print("Client disconnected")


@controller
class WebSocketController:
    handler: WebSocketService = Inject()
    settings: Settings = Inject()

    @get
    def index(self):
        return FileResponse(self.settings.get_resource_path("static", "index.html"))

    @websocket("/chat")
    async def chat(self, context: RequestContext):
        client = context.websocket

        await client.accept()
        print("[open] Client connected")

        await self.handler.handle_client(client)
