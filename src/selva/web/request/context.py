from asgikit.requests import HttpRequest
from asgikit.websockets import WebSocket

__all__ = ["RequestContext"]


class RequestContext:
    __slots__ = ["request", "attributes", "__weakref__"]

    def __init__(self, scope, receive, send):
        if scope["type"] == "http":
            self.request = HttpRequest(scope, receive, send)
        elif scope["type"] == "websocket":
            self.request = WebSocket(scope, receive, send)
        else:
            raise RuntimeError("scope[type] is neither http nor websocket")

        self.attributes = {}

    def __getattr__(self, item):
        return getattr(self.request, item)

    def __getitem__(self, item):
        return self.attributes[item]

    def __setitem__(self, key, value):
        self.attributes[key] = value
