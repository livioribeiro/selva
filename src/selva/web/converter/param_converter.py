from collections.abc import Awaitable
from typing import Protocol, runtime_checkable

__all__ = ("ParamConverter",)


@runtime_checkable
class ParamConverter[T](Protocol[T]):
    """Convert values from and to request parameters

    Request parameters come from path, querystring or headers.
    Request parameters can be extended with `ParamExtractor` implementations
    """

    def from_str(self, data: str) -> T | Awaitable[T]:
        raise NotImplementedError()

    def into_str(self, value: T) -> str | Awaitable[str]:
        return str(value)
