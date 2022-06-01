from pathlib import Path

from asgikit.responses import FileResponse, HttpResponse, HTTPStatus
from asgikit.websockets import WebSocket
from asgikit.errors.websocket import WebSocketDisconnectError

from selva.di import singleton
from selva.web.routing.decorators import controller, get, websocket


@singleton
class WebSocketHandler:
    def __init__(self):
        self.clients: list[WebSocket] = []

    async def broadcast(self, message: str):
        for client in self.clients:
            await client.send_text(message)


@controller("/")
class WebSocketController:
    def __init__(self, handler: WebSocketHandler):
        self.handler = handler

    @get
    def index(self) -> FileResponse:
        return FileResponse(Path(__file__).parent / "index.html")

    @get("/favicon.ico")
    def favicon(self) -> HttpResponse:
        return HttpResponse(status=HTTPStatus.NOT_FOUND)

    @websocket("/chat")
    async def chat(self, client: WebSocket):
        await client.accept()
        print(f"[open] Client connected")

        self.handler.clients.append(client)

        while True:
            try:
                message = await client.receive()
                if message.lower() == "ping":
                    message = "Pong"

                print(f"[message] {message}")
                await self.handler.broadcast(message)
            except WebSocketDisconnectError:
                print("[close] Client disconnected")
                break
