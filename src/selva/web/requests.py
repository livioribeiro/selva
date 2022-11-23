from collections.abc import AsyncGenerator, Awaitable
from enum import Enum
from functools import cache
from typing import Any, Mapping

from starlette.datastructures import URL, Address, FormData, Headers, QueryParams
from starlette.requests import HTTPConnection as StarletteHTTPConnection
from starlette.requests import Request as StarletteRequest
from starlette.types import Receive, Scope, Send

__all__ = ("HTTPMethod", "HTTPConnection", "Request")


class HTTPMethod(str, Enum):
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


class HTTPConnection:
    def __init__(self, scope: Scope):
        self._inner = StarletteHTTPConnection(scope)
        self.scope = scope

    def __getitem__(self, item: str) -> Any:
        return self.scope[item]

    @property
    def url(self) -> URL:
        return self._inner.url

    @property
    def base_url(self) -> URL:
        return self._inner.base_url

    @property
    def path(self) -> str:
        return self.url.path

    @property
    def headers(self) -> Headers:
        return self._inner.headers

    @property
    def query(self) -> QueryParams:
        return self._inner.query_params

    @property
    def cookies(self) -> Mapping[str, str]:
        return self._inner.cookies

    @property
    def client(self) -> Address | None:
        return self._inner.client


class Request(HTTPConnection):
    def __init__(self, scope: Scope, receive: Receive, send: Send):
        super().__init__(scope)
        self._inner = StarletteRequest(scope, receive, send)

    @property
    @cache
    def method(self) -> HTTPMethod:
        return HTTPMethod(self._inner.method)

    def stream(self) -> AsyncGenerator[bytes, None]:
        return self._inner.stream()

    def body(self) -> Awaitable[bytes]:
        return self._inner.body()

    def json(self) -> Awaitable[Any]:
        return self._inner.json()

    def form(self) -> Awaitable[FormData]:
        return self._inner.form()

    def close(self) -> Awaitable:
        return self._inner.close()

    def is_disconnected(self) -> Awaitable[bool]:
        return self._inner.is_disconnected()

    def send_push_promise(self, path: str) -> Awaitable:
        return self._inner.send_push_promise(path)
