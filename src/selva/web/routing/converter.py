from abc import ABCMeta, abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

from selva.di import service

__all__ = ("PathParamConverter", "path_param_converter")

T = TypeVar("T")


@runtime_checkable
class PathParamConverter(Protocol[T], metaclass=ABCMeta):
    @abstractmethod
    async def from_path(self, value: str) -> T:
        pass

    @abstractmethod
    async def to_path(self, obj: T) -> str:
        pass


def path_param_converter(target_type: type):
    def inner(arg: type):
        return service(provides=PathParamConverter[target_type])(arg)

    return inner
