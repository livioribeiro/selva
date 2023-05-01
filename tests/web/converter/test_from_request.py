from pydantic import BaseModel

from selva.web.converter.from_request_impl import (
    RequestContextFromRequest,
    RequestFromRequest,
    WebSocketFromRequest,
    PydanticModelFromRequest,
    PydanticModelListFromRequest,
)

from selva.web.request import Request
from selva.web.context import RequestContext
from selva.web.websocket import WebSocket


def test_request_context_from_request():
    converter = RequestContextFromRequest()
    scope = {"type": "http"}
    context = RequestContext(scope, None, None)

    result = converter.from_request(context, RequestContext, "name")

    assert type(result) == RequestContext
    assert result is context


def test_request_from_request():
    converter = RequestFromRequest()
    scope = {"type": "http"}
    context = RequestContext(scope, None, None)

    result = converter.from_request(context, Request, "name")

    assert type(result) == Request
    assert result is context.request


def test_websocket_from_request():
    converter = WebSocketFromRequest()
    scope = {"type": "websocket"}
    context = RequestContext(scope, None, None)

    result = converter.from_request(context, WebSocket, "name")

    assert type(result) == WebSocket
    assert result is context.websocket


async def test_pydantic_model_from_request():
    class Model(BaseModel):
        field: str

    async def receive():
        return {
            "type": "http.request",
            "body": b'{"field": "value"}',
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }
    context = RequestContext(scope, receive, None)

    converter = PydanticModelFromRequest()

    result = await converter.from_request(context, Model, "name")

    assert type(result) == Model
    assert result.field == "value"


async def test_pydantic_model_list_from_request():
    class Model(BaseModel):
        field: str

    async def receive():
        return {
            "type": "http.request",
            "body": b'[{"field": "value1"}, {"field": "value2"}]',
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }
    context = RequestContext(scope, receive, None)

    converter = PydanticModelListFromRequest()

    result = await converter.from_request(context, list[Model], "name")

    assert type(result) == list
    assert result[0].field == "value1"
    assert result[1].field == "value2"
