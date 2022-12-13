from collections.abc import Awaitable
from typing import Protocol, TypeVar, runtime_checkable

__all__ = ("PathConverter",)

T = TypeVar("T", bound=type)


@runtime_checkable
class PathConverter(Protocol[T]):
    def from_path(self, value: str) -> T | Awaitable[T]:
        raise NotImplementedError()

    def into_path(self, obj: T) -> str | Awaitable[str]:
        return str(obj)
