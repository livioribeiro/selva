import inspect
import warnings
from collections.abc import Callable, Iterable
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
ATTRIBUTE_WEBSOCKET = "__selva_web_websocket__"


# class HandlerType(Enum):
#     GET = HTTPMethod.GET
#     HEAD = HTTPMethod.HEAD
#     POST = HTTPMethod.POST
#     PUT = HTTPMethod.PUT
#     PATCH = HTTPMethod.PATCH
#     DELETE = HTTPMethod.DELETE
#     OPTIONS = HTTPMethod.OPTIONS
#     WEBSOCKET = None
#
#     @property
#     def is_websocket(self) -> bool:
#         return self is HandlerType.WEBSOCKET


class HandlerInfo(NamedTuple):
    mappings: set[tuple[HTTPMethod, str]]


class WebSocketInfo(NamedTuple):
    paths: set[str]


def _check_handler(handler: Callable):
    if not inspect.iscoroutinefunction(handler):
        raise HandlerNotAsyncError(handler)

    assert_params_annotated(handler, skip=1)

    params = list(inspect.signature(handler).parameters.values())
    if len(params) < 1:
        raise HandlerMissingRequestArgumentError(handler)

    req_param = params[0].annotation
    if req_param is not inspect.Signature.empty and req_param is not Request:
        raise HandlerRequestTypeError(handler)


def route(method: HTTPMethod | Iterable[HTTPMethod], path: str | None):
    path = path.strip("/") if path else ""

    if not isinstance(method, Iterable):
        method = {method}
    elif isinstance(method, (tuple, list)):
        method = set(method)

    def wrapper(handler: Callable):
        _check_handler(handler)

        handler_info = getattr(handler, ATTRIBUTE_HANDLER, None)
        if not handler_info:
            handler_info = HandlerInfo(set())

        for m in method:
            if (m, path) in handler_info.mappings:
                warnings.warn(
                    f"Duplicate annotation in handler {handler.__module__}.{handler.__qualname__}: "
                    f"{m} {path}"
                )

            handler_info.mappings.add((m, path))

        setattr(handler, ATTRIBUTE_HANDLER, handler_info)
        return handler

    return wrapper


def _route(method: HTTPMethod | None, path_or_action: str | Callable):
    if isinstance(path_or_action, str):
        path = path_or_action.strip("/")
        action = None
    else:
        path = ""
        action = path_or_action

    wrapper = route(method=[method], path=path)
    return wrapper(action) if action else wrapper


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
    if isinstance(path_or_action, str):
        path = path_or_action.strip("/")
        action = None
    else:
        path = ""
        action = path_or_action

    def wrapper(handler: Callable):
        _check_handler(handler)

        websocket_info = getattr(handler, ATTRIBUTE_WEBSOCKET, None)
        if not websocket_info:
            websocket_info = WebSocketInfo(set())

        websocket_info.paths.add(path)
        setattr(handler, ATTRIBUTE_WEBSOCKET, websocket_info)

        return handler

    return wrapper(action) if action else wrapper
