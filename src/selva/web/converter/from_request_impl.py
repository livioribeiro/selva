from http import HTTPStatus
from typing import Type

import pydantic
from pydantic import BaseModel as PydanticModel

from selva.di.decorator import service
from selva.web.context import RequestContext
from selva.web.converter.from_request import FromRequest
from selva.web.error import HTTPError, HTTPBadRequestError
from selva.web.request import Request
from selva.web.websocket import WebSocket


@service(provides=FromRequest[RequestContext])
class RequestContextFromRequest:
    def from_request(
        self, context: RequestContext, _original_type, _parameter_name
    ) -> RequestContext:
        return context


@service(provides=FromRequest[Request])
class RequestFromRequest:
    def from_request(
        self, context: RequestContext, _original_type, _parameter_name
    ) -> Request:
        if not context.is_http:
            raise TypeError("Not a 'http' request")
        return context.request


@service(provides=FromRequest[WebSocket])
class WebSocketFromRequest:
    def from_request(
        self, context: RequestContext, _original_type, _parameter_name
    ) -> WebSocket:
        if not context.is_websocket:
            raise TypeError("Not a 'websocket' request")
        return context.websocket


@service(provides=FromRequest[PydanticModel])
class PydanticModelFromRequest:
    async def from_request(
        self,
        context: RequestContext,
        original_type: Type[PydanticModel],
        _parameter_name,
    ) -> PydanticModel:
        if not context.method.has_body:
            # TODO: improve error
            raise Exception(
                "Pydantic model parameter on method that does not accept body"
            )

        # TODO: make request body decoding extensible
        if "application/json" in context.headers["content-type"]:
            data = await context.request.json()
        elif "application/x-www-form-urlencoded" in context.headers["content-type"]:
            data = await context.request.form()
        else:
            raise HTTPError(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        try:
            return original_type.model_validate(data)
        except pydantic.ValidationError:
            raise HTTPBadRequestError()


@service(provides=FromRequest[list[PydanticModel]])
class PydanticModelListFromRequest:
    async def from_request(
        self,
        context: RequestContext,
        original_type: Type[list[PydanticModel]],
        _parameter_name,
    ) -> list[PydanticModel]:
        if not context.method.has_body:
            # TODO: improve error
            raise Exception("Pydantic parameter on method that does not accept body")

        if "application/json" in context.headers["content-type"]:
            data = await context.request.json()
        else:
            raise HTTPError(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        adapter = pydantic.TypeAdapter(original_type)

        try:
            return adapter.validate_python(data)
        except pydantic.ValidationError:
            raise HTTPBadRequestError()
