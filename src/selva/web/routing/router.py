from collections import OrderedDict
from collections.abc import Callable
from http import HTTPMethod

import structlog

from selva.web.exception import HTTPNotFoundException
from selva.web.routing.decorator import (
    ATTRIBUTE_HANDLER,
    HandlerInfo,
)
from selva.web.routing.exception import (
    ControllerWithoutDecoratorError,
    DuplicateRouteError,
)
from selva.web.routing.route import Route, RouteMatch

logger = structlog.get_logger()


def _path_with_prefix(path: str, prefix: str):
    path = path.strip("/")
    prefix = prefix.strip("/")
    return f"{prefix}/{path}"


class Router:
    def __init__(self):
        self.routes: OrderedDict[str, Route] = OrderedDict()

    def route(self, action: Callable):
        action_info: HandlerInfo = getattr(action, ATTRIBUTE_HANDLER, None)
        if not action_info:
            raise ControllerWithoutDecoratorError(action)

        action_type = action_info.type
        method: HTTPMethod = action_type.value  # type: ignore
        path = action_info.path.strip("/")
        route_name = f"{action.__module__}.{action.__qualname__}"

        route = Route(method, path, action, route_name)

        for current_route in self.routes.values():
            if (
                current_route.action != route.action
                and current_route.method == route.method
                and current_route.regex == route.regex
            ):
                raise DuplicateRouteError(route.name, current_route.name)

        self.routes[route_name] = route
        logger.debug(
            "action registered",
            action=f"{action.__module__}.{action.__qualname__}",
            method=route.method,
            path=route.path,
        )

    def match(self, method: HTTPMethod | None, path: str) -> RouteMatch | None:
        for route in self.routes.values():
            if (match := route.match(method, path)) is not None:
                return RouteMatch(route, method, path, match)

        return None

    def reverse(self, name: str, **kwargs) -> str:
        if route := self.routes.get(name):
            return route.reverse(**kwargs)

        raise HTTPNotFoundException()
