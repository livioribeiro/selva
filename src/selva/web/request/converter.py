from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from .context import RequestContext

__all__ = ("FromRequestContext",)

T = TypeVar("T")


class FromRequestContext(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    async def from_context(self, context: RequestContext) -> T:
        pass
