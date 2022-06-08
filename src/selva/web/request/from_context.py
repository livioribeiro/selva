from asgikit.headers import Headers
from asgikit.query import Query
from asgikit.requests import HttpRequest
from asgikit.websockets import WebSocket

from selva.di import service

from .context import RequestContext
from .converter import FromRequestContext


@service(provides=FromRequestContext[RequestContext])
class ContextFromRequestContext(FromRequestContext[RequestContext]):
    async def from_context(self, context: RequestContext) -> RequestContext:
        return context


@service(provides=FromRequestContext[HttpRequest])
class RequestFromRequestContext(FromRequestContext[HttpRequest]):
    async def from_context(self, context: RequestContext) -> HttpRequest:
        if context.is_websocket:
            raise TypeError("cannot get HttpRequest from websocket request context")
        return context.request


@service(provides=FromRequestContext[WebSocket])
class WebSocketFromRequestContext(FromRequestContext[WebSocket]):
    async def from_context(self, context: RequestContext) -> WebSocket:
        if context.is_http:
            raise TypeError("cannot get WebSocket from http request context")
        return context.request


@service(provides=FromRequestContext[Headers])
class HeadersFromRequestContext(FromRequestContext[Headers]):
    async def from_context(self, context: RequestContext) -> Headers:
        return context.headers


@service(provides=FromRequestContext[Query])
class QueryFromRequestContext(FromRequestContext[Query]):
    async def from_context(self, context: RequestContext) -> Headers:
        return context.query
