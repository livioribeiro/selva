import inspect
from collections.abc import Callable
from enum import Enum
from http import HTTPMethod
from typing import NamedTuple

from asgikit.requests import Request

from selva.di import service

CONTROLLER_ATTRIBUTE = "__selva_web_controller__"
ACTION_ATTRIBUTE = "__selva_web_action__"


class ControllerInfo(NamedTuple):
    path: str


class ActionType(Enum):
    GET = HTTPMethod.GET
    HEAD = HTTPMethod.HEAD
    POST = HTTPMethod.POST
    PUT = HTTPMethod.PUT
    PATCH = HTTPMethod.PATCH
    DELETE = HTTPMethod.DELETE
    OPTIONS = HTTPMethod.OPTIONS
    WEBSOCKET = None

    @property
    def is_websocket(self) -> bool:
        return self is ActionType.WEBSOCKET


class ActionInfo(NamedTuple):
    type: ActionType
    path: str


def controller(target: type | str):
    if inspect.isclass(target):
        path = ""
        cls = target
    elif isinstance(target, str):
        path = target.strip("/")
        cls = None
    else:
        raise TypeError(f"@controller must be applied to class, '{target}' given")

    def inner(arg: type):
        setattr(arg, CONTROLLER_ATTRIBUTE, ControllerInfo(path))
        return service(arg)

    return inner(cls) if cls else inner


def route(action: Callable = None, /, *, method: HTTPMethod | None, path: str | None):
    path = path.strip("/") if path else ""

    def inner(arg: Callable):
        if not inspect.iscoroutinefunction(arg):
            raise TypeError("Handler method must be async")

        params = list(inspect.signature(arg).parameters.values())
        if len(params) < 2:
            raise TypeError(
                "Handler method must have at least 'self' and 'request' parameters"
            )

        req_param = params[1].annotation
        if req_param is not inspect.Signature.empty and req_param is not Request:
            raise TypeError(
                f"Handler request parameter must be of type "
                f"'{Request.__module__}.{Request.__name__}'"
            )

        if any(p.annotation is inspect.Signature.empty for p in params[2:]):
            raise TypeError("Handler parameters must be typed")

        setattr(arg, ACTION_ATTRIBUTE, ActionInfo(ActionType(method), path))
        return arg

    return inner(action) if action else inner


def _route(method: HTTPMethod | None, path_or_action: str | Callable):
    if isinstance(path_or_action, str):
        path = path_or_action.strip("/")
        action = None
    else:
        path = ""
        action = path_or_action

    return route(action, method=method, path=path)


def get(path_or_action: str | Callable):
    return _route(HTTPMethod.GET, path_or_action)


def post(path_or_action: str | Callable):
    return _route(HTTPMethod.POST, path_or_action)


def put(path_or_action: str | Callable):
    return _route(HTTPMethod.PUT, path_or_action)


def patch(path_or_action: str | Callable):
    return _route(HTTPMethod.PATCH, path_or_action)


def delete(path_or_action: str | Callable):
    return _route(HTTPMethod.DELETE, path_or_action)


def websocket(path_or_action: str | Callable):
    return _route(None, path_or_action)
