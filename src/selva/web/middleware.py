from collections.abc import Awaitable, Callable
from typing import Protocol, runtime_checkable

from asgikit.responses import HttpResponse

from selva.web.request import RequestContext


@runtime_checkable
class Middleware(Protocol):
    async def execute(
        self,
        chain: Callable[[RequestContext], Awaitable[HttpResponse | None]],
        context: RequestContext,
    ) -> HttpResponse | None:
        raise NotImplementedError()
