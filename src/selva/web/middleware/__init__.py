import typing
from collections.abc import Awaitable, Callable
from functools import cache
from typing import Protocol, TypeAlias, runtime_checkable

from asgikit.requests import Request

__all__ = ("Middleware", "CallNext")

from selva.di.container import Container
from selva.web.routing.route import parse_handler_params

CallNext: TypeAlias = Callable[[Request], Awaitable]


@cache
def middleware_services(mid_function: Callable) -> dict[str, tuple[type, str | None]]:
    _, services = parse_handler_params(mid_function)
    return services


class MiddlewareCall:
    def __init__(self, di: Container, function: Callable[..., Awaitable]):
        self.di = di
        self.function = function

    async def __call__(self, callnext: CallNext, request: Request):
        services = {
            name: await self.di.get(service_type, name=service_name)
            for name, (service_type, service_name) in middleware_services(self.function).items()
        }

        await self.function(callnext, request, **services)


@runtime_checkable
class Middleware(Protocol):
    async def __call__(
        self,
        call_next: CallNext,
        request: Request,
    ):
        raise NotImplementedError()
