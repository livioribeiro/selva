from typing import Any

from selva.web.context import RequestContext
from selva.web.converter.from_request import FromRequest
from selva.web.request import Request
from selva.web.websocket import WebSocket


class RequestContextFromRequest(FromRequest[RequestContext]):
    def from_request(self, context: RequestContext) -> RequestContext:
        return context


class RequestFromRequest(FromRequest[Request]):
    def from_request(self, context: RequestContext) -> Request:
        if not context.is_http:
            raise TypeError("Not a 'http' request")
        return context.request


class WebSocketFromRequest(FromRequest[WebSocket]):
    def from_request(self, context: RequestContext) -> WebSocket:
        if not context.is_http:
            raise TypeError("Not a 'websocket' request")
        return context.websocket


class StrFromRequest(FromRequest[str]):
    def from_request(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        return str(value)


class IntFromRequest(FromRequest[int]):
    def from_request(self, value: Any) -> int:
        if isinstance(value, int):
            return value
        return int(value)


class FloatFromRequest(FromRequest[float]):
    def from_request(self, value: Any) -> float:
        if isinstance(value, float):
            return value
        return float(value)


class BoolFromRequest(FromRequest[bool]):
    def from_request(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value in ("1", "true", "True"):
                return True
            if value in ("0", "false", "False"):
                return False
            raise ValueError(value)

        return bool(value)


class ListFromRequest(FromRequest[list]):
    def from_request(self, value: Any) -> list:
        if isinstance(value, list):
            return value
        raise TypeError(type(value))


class DictFromRequest(FromRequest[dict]):
    def from_request(self, value: Any) -> dict:
        if isinstance(value, dict):
            return value
        raise TypeError(type(value))

