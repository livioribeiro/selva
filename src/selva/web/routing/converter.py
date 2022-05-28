from typing import Generic, TypeVar

__all__ = ["PathParameterConverter"]

T = TypeVar("T")


class PathParameterConverter(Generic[T]):
    async def from_path(self, value: str) -> T:
        pass

    async def to_path(self, obj: T) -> str:
        pass
