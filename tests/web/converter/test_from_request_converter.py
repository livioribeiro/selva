from asgikit.requests import Request
from pydantic import BaseModel

from selva.web.converter.converter_impl import (
    RequestDictConverter,
    RequestPydanticConverter,
    RequestPydanticListConverter,
)


async def test_dict_from_request():
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
    converter = RequestDictConverter()

    result = await converter.convert(request, dict)

    assert type(result) == dict
    assert result["field"] == "value"


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
    converter = RequestPydanticConverter()

    result = await converter.convert(request, Model)

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

    request = Request(scope, receive, None)
    converter = RequestPydanticListConverter()

    result = await converter.convert(request, list[Model])

    assert isinstance(result, list)
    assert result[0].field == "value1"
    assert result[1].field == "value2"
