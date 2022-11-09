from collections.abc import Awaitable
from typing import Protocol, TypeVar, runtime_checkable

from selva.web import HttpResponse

__all__ = ("IntoResponse",)

T = TypeVar("T")


@runtime_checkable
class IntoResponse(Protocol[T]):
    def into_response(self, value: T) -> HttpResponse | Awaitable[HttpResponse]:
        raise NotImplementedError()
