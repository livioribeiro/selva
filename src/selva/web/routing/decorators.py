import inspect
from collections.abc import Callable
from enum import Enum
from functools import singledispatch
from typing import NamedTuple

from asgikit.requests import HttpMethod

from selva.di import service

CONTROLLER_ATTRIBUTE = "__selva_web_controller__"
ACTION_ATTRIBUTE = "__selva_web_action__"


class ControllerInfo(NamedTuple):
    path: str


class ActionType(Enum):
    GET = HttpMethod.GET
    POST = HttpMethod.POST
    PUT = HttpMethod.PUT
    PATCH = HttpMethod.PATCH
    DELETE = HttpMethod.DELETE
    WEBSOCKET = None

    @property
    def is_websocket(self) -> bool:
        return self is ActionType.WEBSOCKET


class ActionInfo(NamedTuple):
    type: ActionType
    path: str


@singledispatch
def controller(path):
    # TODO: create exception
    raise ValueError(f"@controller must be applied to class, '{path}' given")


@controller.register
def _(path: str):
    path = path.strip("/")

    def inner(cls: type):
        if not inspect.isclass(cls):
            # TODO: create exception
            raise ValueError(f"@controller must be applied to class, '{cls}' given")

        setattr(cls, CONTROLLER_ATTRIBUTE, ControllerInfo(path))
        return service(cls)

    return inner


@controller.register
def _(cls: type):
    setattr(cls, CONTROLLER_ATTRIBUTE, ControllerInfo(""))
    return service(cls)


def route(action=None, /, *, method: HttpMethod | None, path: str | None):
    path = path.strip("/") if path else ""

    def inner(arg: Callable):
        setattr(arg, ACTION_ATTRIBUTE, ActionInfo(ActionType(method), path))
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
