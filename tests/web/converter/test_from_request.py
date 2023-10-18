from asgikit.requests import Request
from pydantic import BaseModel

from selva.web.converter.from_request_impl import (
    PydanticModelFromRequest,
    PydanticModelListFromRequest,
)


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

    request = Request(scope, receive, None)
    converter = PydanticModelFromRequest()

    result = await converter.from_request(request, Model, "name", None)

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

    context = Request(scope, receive, None)
    converter = PydanticModelListFromRequest()

    result = await converter.from_request(context, list[Model], "name", None)

    assert type(result) == list
    assert result[0].field == "value1"
    assert result[1].field == "value2"
