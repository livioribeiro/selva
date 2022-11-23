from collections.abc import AsyncIterator, Iterable
from typing import Any, Awaitable

from starlette.types import Message, Receive, Scope, Send
from starlette.websockets import WebSocket as StarletteWebsocket

from selva.web.requests import HTTPConnection

__all__ = ("WebSocket",)


class WebSocket(HTTPConnection):
    def __init__(self, scope: Scope, receive: Receive, send: Send):
        super().__init__(scope)
        self._inner = StarletteWebsocket(scope, receive, send)

    def accept(
        self, subprotocol: str = None, headers: Iterable[tuple[bytes, bytes]] = None
    ) -> Awaitable:
        return self._inner.accept(subprotocol, headers)

    def receive(self) -> Awaitable[Message]:
        return self._inner.receive()

    def send(self, message: Message) -> Awaitable:
        return self._inner.send(message)

    def receive_text(self) -> Awaitable[str]:
        return self._inner.receive_text()

    def receive_bytes(self) -> Awaitable[bytes]:
        return self._inner.receive_bytes()

    def receive_json(self, mode: str = "text") -> Awaitable[Any]:
        return self._inner.receive_json(mode)

    def iter_text(self) -> AsyncIterator[str]:
        return self._inner.iter_text()

    def iter_bytes(self) -> AsyncIterator[bytes]:
        return self._inner.iter_bytes()

    def iter_json(self) -> AsyncIterator[Any]:
        return self._inner.iter_json()

    def send_text(self, data: str) -> Awaitable:
        return self._inner.send_text(data)

    def send_bytes(self, data: bytes) -> Awaitable:
        return self._inner.send_bytes(data)

    def send_json(self, data: Any, mode: str = "text") -> Awaitable:
        return self._inner.send_json(data, mode)

    def close(self, code: int = 1000, reason: str = None) -> Awaitable:
        return self._inner.close(code, reason)
