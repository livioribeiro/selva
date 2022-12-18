from abc import ABC
from collections.abc import Awaitable, Callable

from selva.web.contexts import RequestContext
from selva.web.responses import Response

__all__ = ("Middleware",)


class Middleware(ABC):
    def __init__(self):
        # if 'self.set_app' is not called, raise an error
        async def raise_middleware_error(_: RequestContext):
            cls = self.__class__
            class_name = f"{cls.__module__}.{cls.__qualname__}"
            raise RuntimeError(
                f"method 'set_app' was not called on middleware: {class_name}"
            )

        self.app: Callable[
            [RequestContext], Awaitable[Response]
        ] = raise_middleware_error

    async def __call__(self, context: RequestContext) -> Response:
        raise NotImplementedError()

    def set_app(self, app: Callable[[RequestContext], Awaitable[Response]]):
        self.app = app
