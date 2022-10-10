import inspect
from collections import OrderedDict

from asgikit.requests import HttpMethod, HttpRequest
from asgikit.websockets import WebSocket

import selva.logging
from selva.web.errors import NotFoundError

from .decorators import ACTION_ATTRIBUTE, CONTROLLER_ATTRIBUTE, PATH_ATTRIBUTE
from .route import Route, RouteMatch

logger = selva.logging.get_logger()


def _path_with_prefix(path: str, prefix: str):
    path = path.strip("/")
    prefix = prefix.strip("/")
    return f"{prefix}/{path}"


class Router:
    def __init__(self):
        self.routes: OrderedDict[str, Route] = OrderedDict()

    def route(self, controller: type):
        if not hasattr(controller, CONTROLLER_ATTRIBUTE):
            raise ValueError(
                f"{controller.__module__}.{controller.__qualname__}"
                " is not annotated with @controller"
            )

        path_prefix = getattr(controller, PATH_ATTRIBUTE)

        logger.debug(
            "controller registered",
            path=path_prefix or "/",
            cls=controller,
        )

        for name, action in inspect.getmembers(controller, inspect.isfunction):
            action_type = getattr(action, ACTION_ATTRIBUTE, None)
            if not action_type:
                continue

            method = action_type.value
            path = getattr(action, PATH_ATTRIBUTE)
            path = _path_with_prefix(path, path_prefix)
            route_name = f"{controller.__module__}.{controller.__qualname__}:{name}"

            route = Route(method, path, controller, action, route_name)

            if (
                action_type.is_websocket
                and HttpRequest in route.request_params.values()
            ):
                raise TypeError("websocket route cannot receive HttpRequest")

            if (
                not action_type.is_websocket
                and WebSocket in route.request_params.values()
            ):
                raise TypeError("http route cannot receive WebSocket")

            for current_route in self.routes.values():
                # skip route if already registered
                if (
                    current_route.controller == route.controller
                    and current_route.method == route.method
                ):
                    continue

                if (
                    current_route.method == route.method
                    and current_route.regex == route.regex
                ):
                    raise ValueError(
                        f"path for {route.name} clashes with {current_route.name}"
                    )

            self.routes[route_name] = route
            logger.debug(
                "action registered",
                name=route.name,
                method=route.method,
                path=route.path,
                controller=controller,
                action=route.action.__name__,
            )

    def match(self, method: HttpMethod | None, path: str) -> RouteMatch | None:
        for route in self.routes.values():
            if (match := route.match(method, path)) is not None:
                return RouteMatch(route, method, path, match)

        return None

    def reverse(self, name: str, **kwargs) -> str:
        if route := self.routes.get(name):
            return route.reverse(**kwargs)

        raise NotFoundError()
