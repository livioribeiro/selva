from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from asgikit.requests import Request

__all__ = ("Middleware",)


class Middleware(ABC):
    @abstractmethod
    async def __call__(
        self,
        call: Callable[[Request], Awaitable],
        request: Request,
    ):
        raise NotImplementedError()
