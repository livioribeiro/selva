import inspect
from enum import Enum
from typing import Callable

from asgikit.requests import HttpMethod

CONTROLLER_ATTRIBUTE = "__selva_web_controller__"
ACTION_ATTRIBUTE = "__selva_web_action__"
PATH_ATTRIBUTE = "__selva_web_path__"


class ActionType(Enum):
    GET = HttpMethod.GET
    POST = HttpMethod.POST
    PUT = HttpMethod.PUT
    PATCH = HttpMethod.PATCH
    DELETE = HttpMethod.DELETE
    WEBSOCKET = None

    @property
    def is_websocket(self):
        return self is ActionType.WEBSOCKET


def controller(path: str):
    if not isinstance(path, str):
        raise ValueError(f"Invalid argument for @controller: {path}")

    def inner(arg: type):
        if not inspect.isclass(arg):
            raise ValueError("Controller must be a class")

        setattr(arg, CONTROLLER_ATTRIBUTE, True)
        setattr(arg, PATH_ATTRIBUTE, path)
        return arg

    return inner


def route(method: HttpMethod | None, target: str | type):
    if isinstance(target, str):
        action = None
        path = target.strip("/")
    else:
        action = target
        path = ""

    def inner(arg: Callable):
        setattr(arg, ACTION_ATTRIBUTE, ActionType(method))
        setattr(arg, PATH_ATTRIBUTE, path)
        return arg

    return inner(action) if action else inner


def get(path: str | type):
    return route(HttpMethod.GET, path)


def post(path: str | type):
    return route(HttpMethod.POST, path)


def put(path: str | type):
    return route(HttpMethod.PUT, path)


def patch(path: str | type):
    return route(HttpMethod.PATCH, path)


def delete(path: str | type):
    return route(HttpMethod.DELETE, path)


def websocket(path: str | type):
    return route(None, path)
