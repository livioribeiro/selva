from typing import Mapping, ParamSpec, TypeGuard

from starlette.datastructures import URL, Address, Headers, QueryParams
from starlette.types import Receive, Scope, Send

from selva.web.requests import HTTPMethod, Request
from selva.web.websockets import WebSocket

__all__ = ("RequestContext",)

P = ParamSpec("P")


class RequestContext:
    __slots__ = ("scope", "asgi_context", "request", "websocket")

    def __init__(self, scope: Scope, receive: Receive, send: Send):
        assert scope["type"] in ("http", "websocket")

        self.request: Request | None = None
        self.websocket: WebSocket | None = None

        self.scope = scope
        self.asgi_context = scope, receive, send

        if scope["type"] == "http":
            self.request = Request(scope, receive, send)
        else:
            self.websocket = WebSocket(scope, receive, send)

    def __getitem__(self, item):
        return self.scope[item]

    def __setitem__(self, key, value):
        self.scope[key] = value

    @property
    def _http_connection(self) -> Request | WebSocket:
        return self.request or self.websocket

    @property
    def type(self) -> str:
        return self.scope["type"]

    @property
    def is_http(self) -> TypeGuard[Request]:
        return self.type == "http"

    @property
    def is_websocket(self) -> TypeGuard[WebSocket]:
        return self.type == "websocket"

    @property
    def method(self) -> HTTPMethod | None:
        if request := self.request:
            return request.method
        else:
            return None

    @property
    def url(self) -> URL:
        return self._http_connection.url

    @property
    def base_url(self) -> URL:
        return self._http_connection.base_url

    @property
    def path(self) -> str:
        return self.url.path

    @property
    def headers(self) -> Headers:
        return self._http_connection.headers

    @property
    def query(self) -> QueryParams:
        return self._http_connection.query

    @property
    def cookies(self) -> Mapping[str, str]:
        return self._http_connection.cookies

    @property
    def client(self) -> Address | None:
        return self._http_connection.client
