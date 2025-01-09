from http import HTTPMethod

import pytest

from selva.web.routing.decorator import (
    ATTRIBUTE_HANDLER,
    HandlerInfo,
    HandlerType,
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
    "decorator,action_type",
    [
        (get, HandlerType.GET),
        (post, HandlerType.POST),
        (put, HandlerType.PUT),
        (patch, HandlerType.PATCH),
        (delete, HandlerType.DELETE),
        (websocket, HandlerType.WEBSOCKET),
    ],
    ids=["get", "post", "put", "patch", "delete", "websocket"],
)
def test_route_decorator_without_path(decorator, action_type):
    async def handler(req):
        pass

    decorator(handler)

    assert hasattr(handler, ATTRIBUTE_HANDLER)
    assert getattr(handler, ATTRIBUTE_HANDLER) == HandlerInfo(action_type, "")


@pytest.mark.parametrize(
    "decorator,action_type",
    [
        (get, HandlerType.GET),
        (post, HandlerType.POST),
        (put, HandlerType.PUT),
        (patch, HandlerType.PATCH),
        (delete, HandlerType.DELETE),
        (websocket, HandlerType.WEBSOCKET),
    ],
    ids=["get", "post", "put", "patch", "delete", "websocket"],
)
def test_route_decorator_with_path(decorator, action_type):
    async def handler(req):
        pass

    decorator("path")(handler)

    assert hasattr(handler, ATTRIBUTE_HANDLER)
    assert getattr(handler, ATTRIBUTE_HANDLER) == HandlerInfo(action_type, "path")


def test_handler_with_less_than_one_parameter_should_fail():
    async def func0():
        pass

    async def func1(req):
        pass

    with pytest.raises(HandlerMissingRequestArgumentError):
        route(func0, method=HTTPMethod.GET, path="")

    route(func1, method=HTTPMethod.GET, path="")


def test_handler_with_wrong_request_parameter_should_fail():
    async def handler(req: str):
        pass

    with pytest.raises(HandlerRequestTypeError):
        route(handler, method=HTTPMethod.GET, path="")


def test_handler_with_untyped_parameters_should_fail():
    async def handler(req, untyped):
        pass

    with pytest.raises(HandlerUntypedParametersError):
        route(handler, method=HTTPMethod.GET, path="")


def test_non_async_handler_should_fail():
    def handler(req):
        pass

    with pytest.raises(HandlerNotAsyncError):
        route(handler, method=HTTPMethod.GET, path="")
