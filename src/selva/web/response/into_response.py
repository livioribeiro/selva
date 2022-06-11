from collections.abc import Awaitable
from typing import Generic, TypeVar

from asgikit.responses import HttpResponse

__all__ = ("IntoResponse",)

T = TypeVar("T")


class IntoResponse(Generic[T]):
    def into_response(self, value: T) -> HttpResponse | Awaitable[HttpResponse]:
        pass
