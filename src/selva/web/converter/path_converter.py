from abc import ABCMeta, abstractmethod
from collections.abc import Awaitable
from typing import Generic, TypeVar

from selva.di.decorator import service

__all__ = ("PathParamConverter",)

T = TypeVar("T")


class PathParamConverter(Generic[T], metaclass=ABCMeta):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        service(provides=cls.__orig_bases__[0])(cls)

    @abstractmethod
    def from_path(self, value: str) -> T | Awaitable[T]:
        raise NotImplementedError()

    def into_path(self, obj: T) -> str | Awaitable[str]:
        return str(obj)
