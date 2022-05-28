from typing import NamedTuple

from .route_base import BaseRoute


class WebSocketRoute(BaseRoute):
    pass


class WebSocketRouteMatch(NamedTuple):
    route: WebSocketRoute
    path: str
    params: dict[str, str]
