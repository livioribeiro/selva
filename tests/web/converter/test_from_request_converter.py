from asgikit.requests import Request
from pydantic import BaseModel

from selva.web.converter.converter_impl import (
    RequestBodyDictConverter,
    RequestBodyPydanticConverter,
    RequestBodyPydanticListConverter,
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
    converter = RequestBodyDictConverter()

    result = await converter.convert(request.body, dict)

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
    converter = RequestBodyPydanticConverter()

    result = await converter.convert(request.body, Model)

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
    converter = RequestBodyPydanticListConverter()

    result = await converter.convert(request.body, list[Model])

    assert isinstance(result, list)
    assert result[0].field == "value1"
    assert result[1].field == "value2"
