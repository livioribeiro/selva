import inspect
from collections import OrderedDict
from collections.abc import Callable
from http import HTTPMethod

import structlog

from selva._util.package_scan import scan_packages
from selva.web.exception import HTTPNotFoundException
from selva.web.routing.decorator import (
    ATTRIBUTE_HANDLER,
    HandlerInfo,
    ATTRIBUTE_WEBSOCKET,
    WebSocketInfo,
)
from selva.web.routing.exception import (
    DuplicateRouteError,
    HandlerWithoutDecoratorError,
)
from selva.web.routing.route import Route, RouteMatch

logger = structlog.get_logger()


def _is_handler(arg) -> bool:
    return inspect.iscoroutinefunction(arg) and (
        hasattr(arg, ATTRIBUTE_HANDLER) or hasattr(arg, ATTRIBUTE_WEBSOCKET)
    )


class Router:
    def __init__(self):
        self.routes: OrderedDict[str, Route] = OrderedDict()

    def scan(self, *args):
        for item in scan_packages(*args, predicate=_is_handler):
            self.route(item)

    def _check_duplicates(self, route):
        for current_route in self.routes.values():
            if (
                current_route.action != route.action
                and current_route.method == route.method
                and current_route.regex == route.regex
            ):
                raise DuplicateRouteError(route.name, current_route.name)

    def route(self, handler: Callable):
        handler_info: HandlerInfo = getattr(handler, ATTRIBUTE_HANDLER, None)
        websocket_info: WebSocketInfo = getattr(handler, ATTRIBUTE_WEBSOCKET, None)

        if not handler_info and not websocket_info:
            raise HandlerWithoutDecoratorError(handler)

        if handler_info:
            for method, path in handler_info.mappings:
                path = path.strip("/")
                route_name = (
                    f"{method.lower()}.{handler.__module__}.{handler.__qualname__}"
                )
                route = Route(method, path, handler, route_name)
                self._check_duplicates(route)

                self.routes[route_name] = route
                logger.debug(
                    "action registered",
                    action=f"{handler.__module__}.{handler.__qualname__}",
                    method=route.method,
                    path=route.path,
                )

        if websocket_info:
            for path in websocket_info.paths:
                path = path.strip("/")
                route_name = f"websocket.{handler.__module__}.{handler.__qualname__}"
                route = Route(None, path, handler, route_name)
                self._check_duplicates(route)

                self.routes[route_name] = route
                logger.debug(
                    "websocket registered",
                    action=f"{handler.__module__}.{handler.__qualname__}",
                    path=route.path,
                )

    def match(self, method: HTTPMethod | None, path: str) -> RouteMatch | None:
        """Match a path against the routes

        :param method: HTTP method or None for websocket
        :param path: path to match against
        """

        for route in self.routes.values():
            if (match := route.match(method, path)) is not None:
                return RouteMatch(route, method, path, match)

        return None

    def reverse(self, name: str, **kwargs) -> str:
        if route := self.routes.get(name):
            return route.reverse(**kwargs)

        raise HTTPNotFoundException()
