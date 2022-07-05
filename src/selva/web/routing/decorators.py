import inspect
from enum import Enum
from typing import Callable

from asgikit.requests import HttpMethod

from selva.di import service

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


def controller(path_or_cls: str | type):
    if isinstance(path_or_cls, str):
        path = path_or_cls.strip("/")
        cls = None
    elif inspect.isclass(path_or_cls):
        path = ""
        cls = path_or_cls
    else:
        raise ValueError(f"@controller must be applied to class, '{path_or_cls}' given")

    def inner(arg: type):
        if not inspect.isclass(arg):
            raise ValueError(f"@controller must be applied to class, '{arg}' given")

        setattr(arg, CONTROLLER_ATTRIBUTE, True)
        setattr(arg, PATH_ATTRIBUTE, path)

        return service(arg)

    return inner(cls) if cls else inner


def route(action=None, *, method: HttpMethod | None, path: str | None):
    path = path.strip("/") if path else ""

    def inner(arg: Callable):
        setattr(arg, ACTION_ATTRIBUTE, ActionType(method))
        setattr(arg, PATH_ATTRIBUTE, path)
        return arg

    return inner(action) if action else inner


def _route(method: HttpMethod | None, path_or_action: str | Callable):
    if isinstance(path_or_action, str):
        path = path_or_action.strip("/")
        action = None
    else:
        path = ""
        action = path_or_action

    return route(action, method=method, path=path)


def get(path_or_action: str | type):
    return _route(HttpMethod.GET, path_or_action)


def post(path_or_action: str | type):
    return _route(HttpMethod.POST, path_or_action)


def put(path_or_action: str | type):
    return _route(HttpMethod.PUT, path_or_action)


def patch(path_or_action: str | type):
    return _route(HttpMethod.PATCH, path_or_action)


def delete(path_or_action: str | type):
    return _route(HttpMethod.DELETE, path_or_action)


def websocket(path_or_action: str | type):
    return _route(None, path_or_action)
