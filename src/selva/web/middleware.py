from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from asgikit.requests import Request
from asgikit.responses import Response

__all__ = ("Middleware",)


class Middleware(ABC):
    @abstractmethod
    async def __call__(
        self,
        call: Callable[[Request, Response], Awaitable],
        request: Request,
    ):
        raise NotImplementedError()
