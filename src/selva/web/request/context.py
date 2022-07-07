from collections.abc import Awaitable, Callable

from asgikit.requests import HttpRequest
from asgikit.websockets import WebSocket

from selva.utils.maybe_async import maybe_async

__all__ = ("RequestContext",)


class RequestContext:
    __slots__ = ("attributes", "delayed_tasks", "_inner")

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
        self.delayed_tasks = []

    @property
    def request(self):
        return self._inner if self._inner.is_http else None

    @property
    def websocket(self):
        return self._inner if self._inner.is_websocket else None

    def add_delayed_task(self, task: Callable | Awaitable, *args, **kwargs):
        self.delayed_tasks.append(maybe_async(task, *args, **kwargs))

    def __getattr__(self, item):
        return getattr(self._inner, item)

    def __getitem__(self, item):
        return self.attributes[item]

    def __setitem__(self, key, value):
        self.attributes[key] = value
