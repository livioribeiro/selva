from http import HTTPStatus
from pathlib import Path

from selva.di import service
from selva.web import FileResponse, HttpResponse, RequestContext, WebSocket, controller, get, websocket
from selva.web.errors import WebSocketDisconnectError, WebSocketStateError


@service
class WebSocketService:
    def __init__(self):
        self.clients: list[WebSocket] = []

    async def broadcast(self, message: str):
        if message.lower() == "ping":
            message = "Pong"

        disconnected = []
        for client in self.clients:
            try:
                await client.send_text(message)
            except WebSocketStateError:
                disconnected.append(client)

        for disc in disconnected:
            self.clients.remove(disc)


@controller("/")
class WebSocketController:
    def __init__(self, handler: WebSocketService):
        self.handler = handler

    @get
    def index(self) -> FileResponse:
        return FileResponse(Path(__file__).parent / "index.html")

    @get("/favicon.ico")
    def favicon(self) -> HttpResponse:
        return HttpResponse(status=HTTPStatus.NOT_FOUND)

    @websocket("/chat")
    async def chat(self, context: RequestContext):
        client = context.websocket

        await client.accept()
        print("[open] Client connected")

        self.handler.clients.append(client)

        while True:
            try:
                message = await client.receive()
                print(f"[message] {message}")
                await self.handler.broadcast(message)
            except WebSocketDisconnectError:
                print("[close] Client disconnected")
                break
