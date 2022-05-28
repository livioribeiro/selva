from collections.abc import Callable
from enum import Enum

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
    WEBSOCKET = "WEBSOCKET"


def controller(klass: type = None, *, path: str = None):
    if klass and not isinstance(klass, type):
        raise ValueError("Invalid argument for @controller")
    if path and not isinstance(path, str):
        raise ValueError("Invalid argument for @controller")

    def inner(arg: type):
        setattr(arg, CONTROLLER_ATTRIBUTE, arg.__name__)
        setattr(arg, PATH_ATTRIBUTE, path)
        return arg

    return inner(klass) if klass else inner


def route(action: Callable = None, *, method: HttpMethod, path: str = None):
    def inner(arg):
        setattr(arg, ACTION_ATTRIBUTE, ActionType(method))
        setattr(arg, PATH_ATTRIBUTE, path)
        return arg

    return inner(action) if action else inner


def websocket(action: Callable = None, *, path: str = None):
    def inner(arg):
        setattr(arg, ACTION_ATTRIBUTE, ActionType.WEBSOCKET)
        setattr(arg, PATH_ATTRIBUTE, path)
        return arg

    return inner(action) if action else inner


def get(action: Callable = None, *, path: str = None):
    return route(action, method=HttpMethod.GET, path=path)


def post(action: Callable = None, *, path: str = None):
    return route(action, method=HttpMethod.POST, path=path)


def put(action: Callable = None, *, path: str = None):
    return route(action, method=HttpMethod.PUT, path=path)


def patch(action: Callable = None, *, path: str = None):
    return route(action, method=HttpMethod.PATCH, path=path)


def delete(action: Callable = None, *, path: str = None):
    return route(action, method=HttpMethod.DELETE, path=path)
