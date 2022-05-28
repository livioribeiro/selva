from typing import Callable, NamedTuple

from . import BaseRoute


class WebSocketRoute(BaseRoute):
    pass


class WebSocketRouteMatch(NamedTuple):
    route: WebSocketRoute
    path: str
    params: dict[str, str]
