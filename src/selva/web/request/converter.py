from typing import Generic, TypeVar

from asgikit.requests import HttpRequest
from asgikit.websockets import WebSocket

__all__ = ["FromRequest"]

T = TypeVar("T")


class FromRequest(Generic[T]):
    async def from_request(self, request: HttpRequest | WebSocket) -> T:
        pass
