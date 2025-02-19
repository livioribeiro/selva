from typing import Annotated as A

import structlog
from starlette.websockets import WebSocketDisconnect

from selva.web.http import WebSocket
from selva.di import Inject, service
from selva.web import websocket

logger = structlog.get_logger()


@service
class WebSocketService:
    def __init__(self):
        self.clients: dict[str, WebSocket] = {}

    async def handle_websocket(self, websocket: WebSocket):
        client = f"{websocket.client.host}:{websocket.client.port}"
        self.clients[client] = websocket

        logger.info("client connected", client=client)

        while True:
            try:
                message = await websocket.receive_text()
                logger.info("client message", content=message, client=client)
                await self.broadcast(message)
            except WebSocketDisconnect:
                logger.info("client disconnected", client=client)
                del self.clients[client]
                break

    async def broadcast(self, message: str):
        if message.lower() == "ping":
            message = message.replace("i", "o").replace("I", "O")

        for client, ws in self.clients.items():
            try:
                await ws.send_text(message)
            except WebSocketDisconnect:
                del self.clients[client]
                logger.info("client disconnected", client=client)


@websocket("/chat")
async def chat(websocket: WebSocket, handler: A[WebSocketService, Inject]):
    await websocket.accept()
    await handler.handle_websocket(websocket)
