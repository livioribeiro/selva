from abc import ABCMeta, abstractmethod
from collections.abc import Awaitable
from typing import Any, Generic, TypeVar

from selva.di.decorator import service

__all__ = ("FromRequest",)

T = TypeVar("T", bound=type)


class FromRequest(Generic[T], metaclass=ABCMeta):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        service(provides=cls.__orig_bases__[0])(cls)

    @abstractmethod
    def from_request(self, value: Any) -> T | Awaitable[T]:
        raise NotImplementedError()
