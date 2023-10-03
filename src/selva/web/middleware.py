from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from asgikit.requests import Request
from asgikit.responses import Response

__all__ = ("Middleware",)


class Middleware(ABC):
    def __init__(self):
        # if 'self.set_app' is not called, raise an error
        async def call(_request: Request, _response: Response):
            cls = self.__class__
            class_name = f"{cls.__module__}.{cls.__qualname__}"
            raise RuntimeError(
                f"method 'set_app' was not called on middleware: {class_name}"
            )

        self.app: Callable[[Request, Response], Awaitable] = call

    @abstractmethod
    async def __call__(self, request: Request, response: Response) -> Response:
        raise NotImplementedError()

    def set_app(self, app: Callable[[Request, Response], Awaitable]):
        self.app = app
