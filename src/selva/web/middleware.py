from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from selva.web.context import RequestContext
from selva.web.response import Response

__all__ = ("Middleware",)


class Middleware(ABC):
    def __init__(self):
        # if 'self.set_app' is not called, raise an error
        async def call(context: RequestContext):
            cls = self.__class__
            class_name = f"{cls.__module__}.{cls.__qualname__}"
            raise RuntimeError(
                f"method 'set_app' was not called on middleware: {class_name}"
            )

        self.app: Callable[[RequestContext], Awaitable[Response]] = call

    @abstractmethod
    async def __call__(self, context: RequestContext) -> Response:
        raise NotImplementedError()

    def set_app(self, app: Callable[[RequestContext], Awaitable[Response]]):
        self.app = app
