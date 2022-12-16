from selva.di.decorators import service
from selva.web.contexts import RequestContext
from selva.web.converter.from_request import FromRequest
from selva.web.requests import Request
from selva.web.websockets import WebSocket


@service(provides=FromRequest[RequestContext])
class RequestContextFromRequest:
    def from_request(self, context: RequestContext) -> RequestContext:
        return context


@service(provides=FromRequest[Request])
class RequestFromRequest:
    def from_request(self, context: RequestContext) -> Request:
        if not context.is_http:
            raise TypeError("Not a 'http' request")
        return context.request


@service(provides=FromRequest[WebSocket])
class WebSocketFromRequest:
    def from_request(self, context: RequestContext) -> WebSocket:
        if not context.is_http:
            raise TypeError("Not a 'websocket' request")
        return context.websocket
