import inspect
from collections import OrderedDict

from asgikit.requests import HttpMethod, HttpRequest
from asgikit.websockets import WebSocket

from selva.web.errors import NotFoundError

from .decorators import ACTION_ATTRIBUTE, CONTROLLER_ATTRIBUTE, PATH_ATTRIBUTE
from .route import Route, RouteMatch


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
                if (
                    current_route.method == route.method
                    and current_route.regex == route.regex
                ):
                    raise ValueError(
                        f"path for {route.name} clashes with {current_route.name}"
                    )

            self.routes[route_name] = route

    def match(self, method: HttpMethod | None, path: str) -> RouteMatch | None:
        for route in self.routes.values():
            if (match := route.match(method, path)) is not None:
                return RouteMatch(route, method, path, match)

        return None

    def reverse(self, name: str, **kwargs) -> str:
        if route := self.routes.get(name):
            return route.reverse(**kwargs)

        raise NotFoundError()
