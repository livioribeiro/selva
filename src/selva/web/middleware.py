from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable

from asgikit.responses import HttpResponse

from selva.di import service
from selva.web.request import RequestContext

FIRST = 0
LAST = 9999


class Middleware(ABC):
    order = LAST

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if order := getattr(cls, "order", None):
            if order < FIRST:
                cls.order = FIRST
            elif order > LAST:
                cls.order = LAST

        service(cls)

    @abstractmethod
    async def execute(
        self,
        chain: Callable[[RequestContext], Awaitable[HttpResponse | None]],
        context: RequestContext,
    ) -> HttpResponse | None:
        raise NotImplementedError()

    def __lt__(self, other: "Middleware") -> bool:
        return self.order < other.order
