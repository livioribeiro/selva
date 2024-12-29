from collections.abc import Awaitable, Callable
from typing import Protocol, TypeAlias, runtime_checkable

from asgikit.requests import Request

__all__ = ("MiddlewareCall", "CallNext")

from selva.di.container import Container
from selva.di.util import parse_function_services

CallNext: TypeAlias = Callable[[Request], Awaitable]


class MiddlewareCall:
    def __init__(self, di: Container, function: Callable[[CallNext, Request, ...], Awaitable]):
        self.di = di
        self.function = function
        self.services = parse_function_services(self.function, skip=2, require_annotation=False)

    async def __call__(self, callnext: CallNext, request: Request):
        services = {
            name: await self.di.get(service_type, name=service_name)
            for name, (service_type, service_name) in self.services.items()
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
