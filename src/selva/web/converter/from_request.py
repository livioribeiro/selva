from collections.abc import Awaitable
from typing import Protocol, Type, TypeVar, runtime_checkable

from selva.web.context import RequestContext

__all__ = ("FromRequest",)

T = TypeVar("T", bound=type)


@runtime_checkable
class FromRequest(Protocol[T]):
    def from_request(self, context: RequestContext, original: Type[T] | None) -> T | Awaitable[T]:
        raise NotImplementedError()
