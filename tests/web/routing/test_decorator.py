from http import HTTPMethod

import pytest

from selva.web.routing.decorator import (
    ATTRIBUTE_HANDLER,
    ATTRIBUTE_WEBSOCKET,
    HandlerInfo,
    WebSocketInfo,
    delete,
    get,
    patch,
    post,
    put,
    route,
    websocket,
)
from selva.web.routing.exception import (
    HandlerMissingRequestArgumentError,
    HandlerNotAsyncError,
    HandlerRequestTypeError,
    HandlerUntypedParametersError,
)


@pytest.mark.parametrize(
    "decorator,method",
    [
        (get, HTTPMethod.GET),
        (post, HTTPMethod.POST),
        (put, HTTPMethod.PUT),
        (patch, HTTPMethod.PATCH),
        (delete, HTTPMethod.DELETE),
    ],
    ids=["get", "post", "put", "patch", "delete"],
)
def test_route_decorator_without_path(decorator, method):
    async def handler(req):
        pass

    decorator(handler)

    assert hasattr(handler, ATTRIBUTE_HANDLER)
    assert getattr(handler, ATTRIBUTE_HANDLER) == HandlerInfo({(method, "")})


def test_websocket_decorator_without_path():
    async def handler(req):
        pass

    websocket(handler)

    assert hasattr(handler, ATTRIBUTE_WEBSOCKET)
    assert getattr(handler, ATTRIBUTE_WEBSOCKET) == WebSocketInfo({""})


@pytest.mark.parametrize(
    "decorator,method",
    [
        (get, HTTPMethod.GET),
        (post, HTTPMethod.POST),
        (put, HTTPMethod.PUT),
        (patch, HTTPMethod.PATCH),
        (delete, HTTPMethod.DELETE),
    ],
    ids=["get", "post", "put", "patch", "delete"],
)
def test_route_decorator_with_path(decorator, method):
    async def handler(req):
        pass

    decorator("path")(handler)

    assert hasattr(handler, ATTRIBUTE_HANDLER)
    assert getattr(handler, ATTRIBUTE_HANDLER) == HandlerInfo({(method, "path")})


def test_websocket_decorator_with_path():
    async def handler(req):
        pass

    websocket("path")(handler)

    assert hasattr(handler, ATTRIBUTE_WEBSOCKET)
    assert getattr(handler, ATTRIBUTE_WEBSOCKET) == WebSocketInfo({"path"})


def test_handler_with_less_than_one_parameter_should_fail():
    async def func0():
        pass

    async def func1(req):
        pass

    with pytest.raises(HandlerMissingRequestArgumentError):
        route(HTTPMethod.GET, "")(func0)

    route(HTTPMethod.GET, "")(func1)


def test_handler_with_wrong_request_parameter_should_fail():
    async def handler(req: str):
        pass

    with pytest.raises(HandlerRequestTypeError):
        route(HTTPMethod.GET, "")(handler)


def test_handler_with_untyped_parameters_should_fail():
    async def handler(req, untyped):
        pass

    with pytest.raises(HandlerUntypedParametersError):
        route(HTTPMethod.GET, "")(handler)


def test_non_async_handler_should_fail():
    def handler(req):
        pass

    with pytest.raises(HandlerNotAsyncError):
        route(HTTPMethod.GET, "")(handler)


def test_multiple_handler_decorators():
    async def handler(req):
        pass

    get("path")(handler)
    post("another")(handler)

    assert getattr(handler, ATTRIBUTE_HANDLER) == HandlerInfo(
        {
            (HTTPMethod.GET, "path"),
            (HTTPMethod.POST, "another"),
        }
    )


def test_multiple_websocket_decorators():
    async def handler(req):
        pass

    websocket("path")(handler)
    websocket("another")(handler)

    assert getattr(handler, ATTRIBUTE_WEBSOCKET) == WebSocketInfo({"path", "another"})
