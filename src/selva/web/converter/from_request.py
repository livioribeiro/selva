from collections.abc import Awaitable
from typing import Protocol, TypeVar, runtime_checkable

from selva.web.contexts import RequestContext

__all__ = ("FromRequest",)

T = TypeVar("T", bound=type)


@runtime_checkable
class FromRequest(Protocol[T]):
    def from_request(self, context: RequestContext) -> T | Awaitable[T]:
        raise NotImplementedError()
