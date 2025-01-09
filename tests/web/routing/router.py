import pytest

from selva.web.routing.decorator import get
from selva.web.routing.exception import DuplicateRouteError
from selva.web.routing.router import Router


def test_duplicate_route_should_raise_error():
    @get
    async def route1(self, request):
        pass

    @get
    async def route2(self, request):
        pass

    router = Router()

    with pytest.raises(DuplicateRouteError):
        router.route(route1)
        router.route(route2)
