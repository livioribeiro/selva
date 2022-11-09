import inspect
from collections import OrderedDict

from asgikit.requests import HttpMethod, HttpRequest
from asgikit.websockets import WebSocket

import selva.logging
from selva.web.errors import NotFoundError

from .decorators import (
    ACTION_ATTRIBUTE,
    CONTROLLER_ATTRIBUTE,
    ActionInfo,
    ControllerInfo,
)
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
        controller_info: ControllerInfo = getattr(
            controller, CONTROLLER_ATTRIBUTE, None
        )
        if not controller_info:
            # TODO: create exception
            raise ValueError(
                f"{controller.__module__}.{controller.__qualname__}"
                " is not annotated with @controller"
            )

        path_prefix = controller_info.path

        logger.debug(
            "controller registered",
            path=path_prefix or "/",
            cls=controller,
        )

        for name, action in inspect.getmembers(controller, inspect.isfunction):
            action_info: ActionInfo = getattr(action, ACTION_ATTRIBUTE, None)
            if not action_info:
                continue

            action_type = action_info.type
            method: HttpMethod = action_type.value  # type: ignore
            path = action_info.path
            path = _path_with_prefix(path, path_prefix)
            route_name = f"{controller.__module__}.{controller.__qualname__}:{name}"

            route = Route(method, path, controller, action, route_name)

            if (
                action_type.is_websocket
                and HttpRequest in route.request_params.values()
            ):
                # TODO: create exception
                raise TypeError("websocket route cannot receive HttpRequest")

            if (
                not action_type.is_websocket
                and WebSocket in route.request_params.values()
            ):
                # TODO: create exception
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
                    # TODO: create exception
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
