from typing import Callable, NamedTuple, Optional

from asgikit.requests import HttpMethod

from .route_base import BaseRoute


class HttpRoute(BaseRoute):
    def __init__(
        self,
        method: HttpMethod,
        path: str,
        controller: type,
        action: Callable,
        name: str,
    ):
        super().__init__(path, controller, action, name)
        self.method = method

    def match(self, method: HttpMethod, path: str) -> Optional[dict[str, str]]:
        if method == self.method:
            return super().match(path)

        return None


class HttpRouteMatch(NamedTuple):
    route: HttpRoute
    method: HttpMethod
    path: str
    params: dict[str, str]
