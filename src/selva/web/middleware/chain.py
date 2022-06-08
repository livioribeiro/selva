from collections.abc import Callable, Iterable

from selva.web.request import RequestContext


class Chain:
    __slots__ = ("chain", "handler", "context")

    def __init__(
        self,
        chain: Iterable[Callable],
        handler: Callable,
        context: RequestContext,
    ):
        self.chain = iter(chain)
        self.handler = handler
        self.context = context

    async def __call__(self):
        try:
            middleware = next(self.chain)
            return await middleware(self.context, self)
        except StopIteration:
            return await self.handler(self.context)
