from abc import ABCMeta, abstractmethod

from typing import Generic, TypeVar

__all__ = ["PathParamConverter"]

T = TypeVar("T")


class PathParamConverter(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    async def from_path(self, value: str) -> T:
        pass

    @abstractmethod
    async def to_path(self, obj: T) -> str:
        pass
