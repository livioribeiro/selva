from collections.abc import Awaitable, Callable
from typing import Optional, Protocol

from asgikit.responses import HttpResponse

from selva.web.request import RequestContext


class Middleware(Protocol):
    async def execute(
        self,
        chain: Callable[[RequestContext], Awaitable[Optional[HttpResponse]]],
        context: RequestContext,
    ) -> Optional[HttpResponse]:
        pass
