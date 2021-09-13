from collections.abc import Awaitable
from typing import Any, Generic, TypeVar, Union

T = TypeVar("T")


class Lazy(Generic[T]):
    def __init__(self, container, service: type, context: Any = None):
        self._container = container
        self._service = service
        self._context = context
        self._instance = None

    def get(self) -> Union[T, Awaitable[T]]:
        return self._container.get(self._service, context=self._context)
