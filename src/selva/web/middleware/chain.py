import inspect
from collections.abc import Callable

from selva.di import Container
from selva.web.request import RequestContext


class Chain:
    def __init__(
        self,
        di: Container,
        chain: list[Callable],
        end_handler: Callable,
        context: RequestContext,
    ):
        self.di = di
        self.chain = iter(chain)
        self.handler = end_handler
        self.context = context

    async def __call__(self):
        try:
            middleware = next(self.chain)
            if inspect.isclass(middleware):
                middleware = await self.di.get(middleware)
            return await middleware(self.context, self)
        except StopIteration:
            return await self.handler(self.context)
