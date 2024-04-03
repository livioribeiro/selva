import pytest

from selva.web.routing.decorator import controller, get
from selva.web.routing.exception import (
    ControllerWithoutDecoratorError,
    DuplicateRouteError,
)
from selva.web.routing.router import Router


def test_controller_without_decorator_should_raise_error():
    class Controller:
        pass

    router = Router()

    with pytest.raises(ControllerWithoutDecoratorError):
        router.route(Controller)


def test_duplicate_route_should_raise_error():
    @controller
    class Controller:
        @get
        async def route1(self, request):
            pass

        @get
        async def route2(self, request):
            pass

    router = Router()

    with pytest.raises(DuplicateRouteError):
        router.route(Controller)
