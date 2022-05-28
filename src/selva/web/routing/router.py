import inspect
from collections import OrderedDict
from typing import Callable, Optional

from asgikit.requests import HttpMethod, HttpRequest
from asgikit.websockets import WebSocket

from ..exceptions import RouteNotFoundError
from .decorators import (
    ACTION_ATTRIBUTE,
    CONTROLLER_ATTRIBUTE,
    PATH_ATTRIBUTE,
    ActionType,
)
from .route_http import HttpRoute, HttpRouteMatch
from .route_websocket import WebSocketRoute, WebSocketRouteMatch


def _name_transform(name: str) -> str:
    yield name[0].lower()
    for letter in name[1:]:
        if letter.isupper():
            yield "-"
            yield letter.lower()
        else:
            yield letter


def _controller_path(controller_class: type) -> str:
    return "".join(_name_transform(controller_class.__name__))


def _get_action_path(action: Callable, path_prefix: str = "") -> str:
    path = getattr(action, PATH_ATTRIBUTE, None)
    if path is not None:
        return _path_with_prefix(path, path_prefix)

    name = action.__name__
    path = "" if name == "index" else name.replace("_", "-")
    path = _path_with_prefix(path, path_prefix)

    parameters = inspect.signature(action).parameters.keys()
    param_names = (
        f"{{{parameter}}}" for parameter in parameters if parameter != "self"
    )
    return "/".join([path, *param_names])


def _path_with_prefix(path: str, prefix: str):
    return prefix.removeprefix("/").removesuffix("/") + "/" + path.removeprefix("/")


class Router:
    def __init__(self):
        self.__http_routes: OrderedDict[str, HttpRoute] = OrderedDict()
        self.__websocket_routes: OrderedDict[str, WebSocketRoute] = OrderedDict()

    def route(self, controller: type):
        if not hasattr(controller, CONTROLLER_ATTRIBUTE):
            raise ValueError(
                f"{controller.__qualname__} is not annotated with @controller"
            )

        path_prefix = getattr(controller, PATH_ATTRIBUTE, None)
        if path_prefix is None:
            path_prefix = _controller_path(controller)

        for name, action in inspect.getmembers(controller, inspect.isfunction):
            action_info = getattr(action, ACTION_ATTRIBUTE, None)
            if not action_info:
                continue

            action_name = f"{controller.__name__}:{name}"
            action_path = _get_action_path(action, path_prefix)

            if action_info is ActionType.WEBSOCKET:
                if name in self.__websocket_routes:
                    raise ValueError(f"route '{name}' is already defined")

                route = WebSocketRoute(action_path, controller, action, action_name)
                self.__websocket_routes[name] = route
            else:
                method = action_info.value
                if name in self.__http_routes:
                    raise ValueError(f"route '{name}' is already defined")

                route = HttpRoute(method, action_path, controller, action, action_name)
                self.__http_routes[name] = route

    def match_http(self, request: HttpRequest) -> Optional[HttpRouteMatch]:
        for route in self.__http_routes.values():
            if (match := route.match(request.method, request.path)) is not None:
                return HttpRouteMatch(route, request.method, request.path, match)

        return None

    def match_websocket(self, websocket: WebSocket) -> Optional[WebSocketRouteMatch]:
        for route in self.__websocket_routes.values():
            if (match := route.match(websocket.path)) is not None:
                return WebSocketRouteMatch(route, websocket.path, match)

        return None

    def reverse(self, name: str, **kwargs) -> str:
        route = self.__http_routes.get(name) or self.__websocket_routes.get(name)
        if not route:
            raise RouteNotFoundError()

        return route.reverse(**kwargs)
