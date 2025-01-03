from http import HTTPStatus

import pytest
from asgikit.requests import Request
from pydantic import BaseModel

from selva.web.converter.converter_impl import (
    RequestBodyJsonConverter,
    RequestBodyFormConverter,
    RequestBodyPydanticConverter,
    RequestBodyPydanticListConverter,
)
from selva.web.exception import HTTPException


async def test_json_from_request():
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
    converter = RequestBodyJsonConverter()

    result = await converter.convert(request.body, dict)

    assert type(result) == dict
    assert result["field"] == "value"


async def test_json_from_request_with_wrong_content_type_should_fail():
    async def receive():
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/x-www-form-urlencoded")],
    }

    request = Request(scope, receive, None)
    converter = RequestBodyJsonConverter()

    with pytest.raises(HTTPException) as err:
        await converter.convert(request.body, dict)

    assert err.value.status == HTTPStatus.UNSUPPORTED_MEDIA_TYPE


async def test_form_from_request():
    async def receive():
        return {
            "type": "http.request",
            "body": b"field1=value1&field2=value2",
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/x-www-form-urlencoded")],
    }

    request = Request(scope, receive, None)
    converter = RequestBodyFormConverter()

    result = await converter.convert(request.body, dict)

    assert type(result) == dict
    assert result["field1"] == "value1" and result["field2"] == "value2"


async def test_form_from_request_with_wrong_content_type_should_fail():
    async def receive():
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/json")],
    }

    request = Request(scope, receive, None)
    converter = RequestBodyFormConverter()

    with pytest.raises(HTTPException) as err:
        await converter.convert(request.body, dict)

    assert err.value.status == HTTPStatus.UNSUPPORTED_MEDIA_TYPE


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
