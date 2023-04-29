from collections.abc import Awaitable
from typing import Protocol, TypeVar, runtime_checkable

__all__ = ("FromRequestParam",)

T = TypeVar("T")


@runtime_checkable
class FromRequestParam(Protocol[T]):
    """Convert values from and to path parameters"""

    def from_request_param(self, value: str) -> T | Awaitable[T]:
        raise NotImplementedError()
