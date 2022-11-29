from collections.abc import Awaitable, Callable, Iterable
from typing import Protocol, runtime_checkable

from selva.web.contexts import RequestContext
from selva.web.responses import Response

__all__ = ("CallChain", "Middleware", "MiddlewareChain")


CallChain = Callable[[RequestContext], Awaitable[Response]]


@runtime_checkable
class Middleware(Protocol):
    async def __call__(
        self,
        context: RequestContext,
        chain: Callable[[RequestContext], Awaitable[Response]],
    ) -> Response | None:
        raise NotImplementedError()


class MiddlewareChain:
    __slots__ = ("chain", "handler", "iter")

    def __init__(
        self,
        chain: Iterable[Middleware],
        handler: CallChain,
    ):
        self.chain = chain
        self.handler = handler
        self.iter = iter(chain)

    async def __call__(self, context: RequestContext) -> Response:
        try:
            middleware = next(self.iter)
            return await middleware(context, self)
        except StopIteration:
            response = await self.handler(context)
            return response
