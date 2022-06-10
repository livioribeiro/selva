from asgikit.requests import HttpRequest
from asgikit.websockets import WebSocket

__all__ = ("RequestContext",)


class RequestContext:
    __slots__ = ("attributes", "_inner", "__weakref__")

    def __init__(self, scope, receive, send):
        if scope["type"] == "http":
            self._inner = HttpRequest(scope, receive, send)
        elif scope["type"] == "websocket":
            self._inner = WebSocket(scope, receive, send)
        else:
            raise RuntimeError(
                f"scope[type] is neither http nor websocket ({scope['type']})"
            )

        self.attributes = {}

    @property
    def request(self):
        return self._inner if self._inner.is_http else None

    @property
    def websocket(self):
        return self._inner if self._inner.is_websocket else None

    def __getattr__(self, item):
        return getattr(self._inner, item)

    def __getitem__(self, item):
        return self.attributes[item]

    def __setitem__(self, key, value):
        self.attributes[key] = value
