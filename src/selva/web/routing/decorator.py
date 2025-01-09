import inspect
from collections.abc import Callable
from enum import Enum
from http import HTTPMethod
from typing import NamedTuple

from asgikit.requests import Request

from selva.web.handler.parse import assert_params_annotated
from selva.web.routing.exception import (
    HandlerMissingRequestArgumentError,
    HandlerNotAsyncError,
    HandlerRequestTypeError,
)

ATTRIBUTE_HANDLER = "__selva_web_action__"


class HandlerType(Enum):
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
        return self is HandlerType.WEBSOCKET


class HandlerInfo(NamedTuple):
    type: HandlerType
    path: str


def route(handler: Callable = None, /, *, method: HTTPMethod | None, path: str | None):
    path = path.strip("/") if path else ""

    def inner(arg: Callable):
        if not inspect.iscoroutinefunction(arg):
            raise HandlerNotAsyncError(handler)

        assert_params_annotated(arg, skip=1)

        params = list(inspect.signature(arg).parameters.values())
        if len(params) < 1:
            raise HandlerMissingRequestArgumentError(handler)

        req_param = params[0].annotation
        if req_param is not inspect.Signature.empty and req_param is not Request:
            raise HandlerRequestTypeError(handler)

        setattr(arg, ATTRIBUTE_HANDLER, HandlerInfo(HandlerType(method), path))
        return arg

    return inner(handler) if handler else inner


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
