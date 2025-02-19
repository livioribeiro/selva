from http import HTTPStatus
from typing import Literal

import pytest
from pydantic import BaseModel

from selva.web.converter.converter_impl import (
    RequestPydanticConverter,
    RequestPydanticListConverter,
)
from selva.web.exception import HTTPException
from selva.web.http import Request


async def test_pydantic_model_from_json_request():
    class Model(BaseModel):
        field1: str
        field2: int

    async def receive():
        return {
            "type": "http.request",
            "body": b'{"field1": "value", "field2": 1}',
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

    assert type(result) is Model
    assert result.field1 == "value"
    assert result.field2 == 1


async def test_pydantic_model_from_form_request():
    class Model(BaseModel):
        field1: str
        field2: int

    async def receive():
        return {
            "type": "http.request",
            "body": b"field1=value&field2=1",
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/x-www-form-urlencoded")],
    }

    request = Request(scope, receive, None)
    converter = RequestPydanticConverter()

    result = await converter.convert(request, Model)

    assert type(result) is Model
    assert result.field1 == "value"
    assert result.field2 == 1


async def test_pydantic_model_with_wrong_content_type_should_fail():
    class Model(BaseModel):
        field1: str
        field2: int

    async def receive():
        return {
            "type": "http.request",
            "body": b'"value",1',
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"text/csv")],
    }

    request = Request(scope, receive, None)
    converter = RequestPydanticConverter()

    with pytest.raises(HTTPException) as err:
        await converter.convert(request, Model)
    assert err.value.status == HTTPStatus.UNSUPPORTED_MEDIA_TYPE


async def test_pydantic_model_with_invalid_data_should_fail():
    class Model(BaseModel):
        field: Literal["value"]

    async def receive():
        return {
            "type": "http.request",
            "body": b'{"field": "wrong"}',
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    request = Request(scope, receive, None)
    converter = RequestPydanticConverter()

    with pytest.raises(HTTPException) as err:
        await converter.convert(request, Model)
    assert err.value.status == HTTPStatus.BAD_REQUEST


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


async def test_pydantic_model_list_with_wrong_content_type_should_fail():
    class Model(BaseModel):
        field: str

    async def receive():
        return {
            "type": "http.request",
            "body": b"value1\nvalue2",
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"text/csv")],
    }

    request = Request(scope, receive, None)
    converter = RequestPydanticListConverter()

    with pytest.raises(HTTPException) as err:
        await converter.convert(request, list[Model])

    assert err.value.status == HTTPStatus.UNSUPPORTED_MEDIA_TYPE


async def test_pydantic_model_list_with_invalid_data_should_fail():
    class Model(BaseModel):
        field: Literal["value"]

    async def receive():
        return {
            "type": "http.request",
            "body": b'[{"field": "wrong"}]',
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    request = Request(scope, receive, None)
    converter = RequestPydanticListConverter()

    with pytest.raises(HTTPException) as err:
        await converter.convert(request, list[Model])
    assert err.value.status == HTTPStatus.BAD_REQUEST
