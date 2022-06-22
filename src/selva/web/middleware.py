from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from asgikit.responses import HttpResponse

from selva.web.request import RequestContext


class Middleware(ABC):
    @abstractmethod
    async def execute(
        self,
        chain: Callable[[RequestContext], Awaitable[HttpResponse | None]],
        context: RequestContext,
    ) -> HttpResponse | None:
        raise NotImplementedError()
