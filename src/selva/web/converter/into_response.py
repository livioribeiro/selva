from collections.abc import Awaitable
from typing import Protocol, TypeVar, runtime_checkable

from starlette.responses import Response

__all__ = ("IntoResponse",)

T = TypeVar("T")


@runtime_checkable
class IntoResponse(Protocol[T]):
    def into_response(self, value: T) -> Response | Awaitable[Response]:
        raise NotImplementedError()
