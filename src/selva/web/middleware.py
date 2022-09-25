from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from asgikit.responses import HttpResponse

from selva.di import service
from selva.web.request import RequestContext


class Middleware(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        service(cls)

    @abstractmethod
    async def execute(
        self,
        chain: Callable[[RequestContext], Awaitable[HttpResponse | None]],
        context: RequestContext,
    ) -> HttpResponse | None:
        raise NotImplementedError()
