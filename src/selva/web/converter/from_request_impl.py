from http import HTTPStatus
from typing import Type

from selva.di.decorator import service
from selva.web.context import RequestContext
from selva.web.converter.from_request import FromRequest
from selva.web.error import HTTPError
from selva.web.request import Request
from selva.web.websocket import WebSocket

from pydantic import BaseModel as PydanticModel


@service(provides=FromRequest[RequestContext])
class RequestContextFromRequest:
    def from_request(self, context: RequestContext, _original) -> RequestContext:
        return context


@service(provides=FromRequest[Request])
class RequestFromRequest:
    def from_request(self, context: RequestContext, _original) -> Request:
        if not context.is_http:
            raise TypeError("Not a 'http' request")
        return context.request


@service(provides=FromRequest[WebSocket])
class WebSocketFromRequest:
    def from_request(self, context: RequestContext, _original) -> WebSocket:
        if not context.is_http:
            raise TypeError("Not a 'websocket' request")
        return context.websocket


if PydanticModel:
    @service(provides=FromRequest[PydanticModel])
    class PydanticModelFromRequest:
        async def from_request(self, context: RequestContext, original: Type[PydanticModel]) -> PydanticModel:
            if not context.method.has_body:
                # TODO: improve error
                raise Exception("Pydantic model parameter on method that does not accept body")

            if "application/json" in context.headers["content-type"]:
                data = await context.request.json()
            elif "application/x-www-form-urlencoded" in context.headers["content-type"]:
                data = await context.request.form()
            else:
                raise HTTPError(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

            return original.parse_obj(data)

