import pytest
from asgikit.requests import Request
from pydantic import BaseModel

from selva.di.container import Container
from selva.web.converter import Form, Json
from selva.web.converter.converter_impl import (
    RequestBodyFormConverter,
    RequestBodyJsonConverter,
    RequestBodyPydanticListConverter,
)
from selva.web.converter.error import (
    FromBodyOnWrongHttpMethodError,
    MissingConverterImplError,
    MissingRequestParamExtractorImplError,
    PathParamNotFoundError,
)
from selva.web.converter.from_request import FromRequest
from selva.web.converter.from_request_impl import (
    BodyFromRequest,
    CookieParamFromRequest,
    HeaderParamFromRequest,
    PathParamFromRequest,
    QueryParamFromRequest,
)
from selva.web.converter.param_converter_impl import StrParamConverter
from selva.web.converter.param_extractor import (
    FromCookie,
    FromHeader,
    FromPath,
    FromQuery,
)
from selva.web.converter.param_extractor_impl import (
    FromCookieExtractor,
    FromHeaderExtractor,
    FromPathExtractor,
    FromQueryExtractor,
)


async def test_body_from_request_wrong_http_method_should_fail(ioc: Container):
    ioc.register(RequestBodyJsonConverter)
    from_request = BodyFromRequest(ioc)

    async def receive():
        return {
            "type": "http.request",
            "body": b'{"field": "value"}',
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "GET",
        "headers": [(b"content-type", b"application/json")],
    }

    request = Request(scope, receive, None)

    with pytest.raises(FromBodyOnWrongHttpMethodError):
        await from_request.from_request(request, Json, "parameter", None, False)


async def test_body_from_request(ioc: Container):
    ioc.register(RequestBodyJsonConverter)
    from_request = BodyFromRequest(ioc)

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

    result = await from_request.from_request(request, Json, "parameter", None, False)
    assert isinstance(result, dict)
    assert result["field"] == "value"


async def test_body_list_from_request(ioc: Container):
    ioc.register(RequestBodyPydanticListConverter)
    from_request = BodyFromRequest(ioc)

    class MyModel(BaseModel):
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

    result = await from_request.from_request(
        request, list[MyModel], "parameter", None, False
    )
    assert isinstance(result, list)
    assert result == [
        MyModel.model_validate({"field": "value1"}),
        MyModel.model_validate({"field": "value2"}),
    ]


async def test_form_from_request(ioc: Container):
    ioc.register(RequestBodyFormConverter)
    from_request = BodyFromRequest(ioc)

    async def receive():
        return {
            "type": "http.request",
            "body": b"field=value",
            "more_body": False,
        }

    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"content-type", b"application/x-www-form-urlencoded")],
    }

    request = Request(scope, receive, None)

    result = await from_request.from_request(request, Form, "parameter", None, False)
    assert isinstance(result, dict)
    assert result["field"] == "value"


async def test_missing_converter_should_fail(ioc: Container):
    from_request = BodyFromRequest(ioc)

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

    with pytest.raises(MissingConverterImplError):
        await from_request.from_request(request, Json, "parameter", None, False)


async def test_path_param_from_request(ioc: Container):
    ioc.define(Container, ioc)
    ioc.register(StrParamConverter)
    ioc.register(PathParamFromRequest)
    ioc.register(FromPathExtractor)

    from_request = await ioc.get(FromRequest[FromPath])

    scope = {"type": "http", "method": "GET"}
    request = Request(scope, None, None)
    request.attributes["path_params"] = {"param": "value"}

    result = await from_request.from_request(request, str, "param", FromPath, False)
    assert result == "value"


async def test_path_param_from_request_missing_param_should_fail(ioc: Container):
    ioc.define(Container, ioc)
    ioc.register(StrParamConverter)
    ioc.register(PathParamFromRequest)
    ioc.register(FromPathExtractor)

    from_request = await ioc.get(FromRequest[FromPath])

    scope = {"type": "http", "method": "GET"}
    request = Request(scope, None, None)
    request.attributes["path_params"] = {}

    with pytest.raises(PathParamNotFoundError):
        await from_request.from_request(request, str, "param", FromPath, False)


async def test_query_param_from_request(ioc: Container):
    ioc.define(Container, ioc)
    ioc.register(StrParamConverter)
    ioc.register(QueryParamFromRequest)
    ioc.register(FromQueryExtractor)

    from_request = await ioc.get(FromRequest[FromQuery])

    scope = {"type": "http", "method": "GET", "query_string": b"param=value"}
    request = Request(scope, None, None)

    result = await from_request.from_request(request, str, "param", FromQuery, False)
    assert result == "value"


async def test_header_param_from_request(ioc: Container):
    ioc.define(Container, ioc)
    ioc.register(StrParamConverter)
    ioc.register(HeaderParamFromRequest)
    ioc.register(FromHeaderExtractor)

    from_request = await ioc.get(FromRequest[FromHeader])

    scope = {"type": "http", "method": "GET", "headers": [(b"param", b"value")]}
    request = Request(scope, None, None)

    result = await from_request.from_request(request, str, "param", FromHeader, False)
    assert result == "value"


async def test_cookie_param_from_request(ioc: Container):
    ioc.define(Container, ioc)
    ioc.register(StrParamConverter)
    ioc.register(CookieParamFromRequest)
    ioc.register(FromCookieExtractor)

    from_request = await ioc.get(FromRequest[FromCookie])

    scope = {"type": "http", "method": "GET", "headers": [(b"cookie", b"param=value")]}
    request = Request(scope, None, None)

    result = await from_request.from_request(request, str, "param", FromCookie, False)
    assert result == "value"


async def test_missing_param_extractor_should_fail(ioc: Container):
    ioc.define(Container, ioc)
    ioc.register(StrParamConverter)
    ioc.register(PathParamFromRequest)

    from_request = await ioc.get(FromRequest[FromPath])

    scope = {
        "type": "http",
        "method": "GET",
    }
    request = Request(scope, None, None)
    request.attributes["path_params"] = {"param": "value"}

    with pytest.raises(MissingRequestParamExtractorImplError):
        await from_request.from_request(request, str, "param", FromPath, False)
