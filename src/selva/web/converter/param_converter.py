from collections.abc import Awaitable
from typing import Protocol, TypeVar, runtime_checkable

__all__ = ("RequestParamConverter",)

T = TypeVar("T")


@runtime_checkable
class RequestParamConverter(Protocol[T]):
    """Convert values from and to path parameters"""

    def convert(self, value: str) -> T | Awaitable[T]:
        raise NotImplementedError()

    def convert_back(self, obj: T) -> str | Awaitable[str]:
        return str(obj)
