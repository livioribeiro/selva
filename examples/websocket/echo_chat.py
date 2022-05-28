from pathlib import Path

from asgikit.responses import FileResponse, HttpResponse, HTTPStatus
from asgikit.websockets import WebSocket
from asgikit.errors.websocket import WebSocketDisconnectError

from selva.web.application import Application
from selva.web.routing.decorators import controller, get, websocket


@controller(path="/")
class Controller:
    @get
    def index(self) -> FileResponse:
        return FileResponse(Path(__file__).parent / "index.html")

    @get(path="/favicon.ico")
    def favicon(self) -> HttpResponse:
        return HttpResponse(status=HTTPStatus.NOT_FOUND)

    @websocket(path="/chat")
    async def chat(self, client: WebSocket):
        await client.accept()
        print(f"[open] Client connected")

        while True:
            try:
                message = await client.receive()
                if message.lower() == "Ping":
                    message = "Pong"

                print(f"[message] {message}")
                await client.send_text(message)
            except WebSocketDisconnectError:
                print("[close] Client disconnected")
                break


app = Application()
app.controllers(Controller)
