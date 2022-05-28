from asgikit.headers import Headers
from asgikit.requests import HttpRequest
from asgikit.websockets import WebSocket

from selva.di.decorators import singleton

from .converter import FromRequest


@singleton(provides=FromRequest[HttpRequest])
class RequestFromRequest(FromRequest[HttpRequest]):
    async def from_request(self, request: HttpRequest | WebSocket) -> HttpRequest:
        return request


@singleton(provides=FromRequest[WebSocket])
class WebSocketFromRequest(FromRequest[WebSocket]):
    async def from_request(self, request: HttpRequest | WebSocket) -> WebSocket:
        return request


@singleton(provides=FromRequest[Headers])
class HeadersFromRequest(FromRequest[Headers]):
    async def from_request(self, request: HttpRequest | WebSocket) -> Headers:
        return request.headers
