from http import HTTPMethod

import pytest

from selva.web.routing.decorator import (
    ATTRIBUTE_HANDLER,
    CONTROLLER_ATTRIBUTE,
    HandlerInfo,
    HandlerType,
    ControllerInfo,
    controller,
    delete,
    get,
    patch,
    post,
    put,
    route,
    websocket,
)


def test_controller_decorator_without_path():
    class Controller:
        pass

    controller(Controller)

    assert hasattr(Controller, CONTROLLER_ATTRIBUTE)
    assert getattr(Controller, CONTROLLER_ATTRIBUTE) == ControllerInfo("")


def test_controller_decorator_with_path():
    class Controller:
        pass

    controller("path")(Controller)

    assert hasattr(Controller, CONTROLLER_ATTRIBUTE)
    assert getattr(Controller, CONTROLLER_ATTRIBUTE) == ControllerInfo("path")


def test_controller_decorator_on_non_class_should_fail():
    async def func():
        pass

    with pytest.raises(TypeError):
        controller(func)


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
    class Controller:
        async def handler(self, req):
            pass

    decorator(Controller.handler)

    assert hasattr(Controller.handler, ATTRIBUTE_HANDLER)
    assert getattr(Controller.handler, ATTRIBUTE_HANDLER) == HandlerInfo(action_type, "")


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
    class Controller:
        async def handler(self, req):
            pass

    decorator("path")(Controller.handler)

    assert hasattr(Controller.handler, ATTRIBUTE_HANDLER)
    assert getattr(Controller.handler, ATTRIBUTE_HANDLER) == HandlerInfo(
        action_type, "path"
    )


def test_handler_with_less_than_one_parameter_should_fail():
    class Controller:
        async def func0(self):
            pass

        async def func1(self, req):
            pass

    with pytest.raises(
        TypeError,
        match="Handler method must have at least 'self' and 'request' parameters",
    ):
        route(Controller.func0, method=HTTPMethod.GET, path="")

    route(Controller.func1, method=HTTPMethod.GET, path="")


def test_handler_with_wrong_request_parameter_should_fail():
    class Controller:
        async def handler(self, req: str):
            pass

    with pytest.raises(
        TypeError,
        match="Handler request parameter must be of type 'asgikit.requests.Request'",
    ):
        route(Controller.handler, method=HTTPMethod.GET, path="")


def test_handler_with_untyped_parameters_should_fail():
    class Controller:
        async def handler(self, req, untyped):
            pass

    with pytest.raises(TypeError, match="Handler parameters must be typed"):
        route(Controller.handler, method=HTTPMethod.GET, path="")


def test_non_async_handler_should_fail():
    def handler(req):
        pass

    with pytest.raises(TypeError, match="Handler method must be async"):
        route(handler, method=HTTPMethod.GET, path="")
