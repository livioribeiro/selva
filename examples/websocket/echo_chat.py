from pathlib import Path

from asgikit.responses import FileResponse, HttpResponse, HTTPStatus
from asgikit.websockets import WebSocket
from asgikit.errors.websocket import WebSocketDisconnectError

from selva.web.application import Application
from selva.web.routing.decorators import controller, get, websocket


@controller("/")
class Controller:
    @get("/")
    def index(self) -> FileResponse:
        return FileResponse(Path(__file__).parent / "index.html")

    @get("/favicon.ico")
    def favicon(self) -> HttpResponse:
        return HttpResponse(status=HTTPStatus.NOT_FOUND)

    @websocket("/chat")
    async def chat(self, client: WebSocket):
        await client.accept()
        print(f"[open] Client connected")

        while True:
            try:
                message = await client.receive()
                if message.lower() == "ping":
                    message = "Pong"

                print(f"[message] {message}")
                await client.send_text(message)
            except WebSocketDisconnectError:
                print("[close] Client disconnected")
                break


app = Application()
app.controllers(Controller)
