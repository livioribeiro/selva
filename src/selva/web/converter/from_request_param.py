from collections.abc import Awaitable
from typing import Protocol, TypeVar, runtime_checkable

__all__ = ("FromRequestParam",)

T = TypeVar("T")


@runtime_checkable
class FromRequestParam(Protocol[T]):
    """Convert values from and to request parameters

    Request parameters come from path, querystring, headers.
    Request parameters can be extended with `ParamExtractor` implementations
    """

    def from_param(self, value: str) -> T | Awaitable[T]:
        raise NotImplementedError()

    def into_str(self, data: T) -> str | Awaitable[str]:
        return str(data)
