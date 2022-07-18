from collections.abc import Awaitable
from typing import Generic, TypeVar

from selva.di import service
from selva.web import HttpResponse

__all__ = ("IntoResponse",)

T = TypeVar("T")


class IntoResponse(Generic[T]):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        service(provides=cls.__orig_bases__[0])(cls)

    def into_response(self, value: T) -> HttpResponse | Awaitable[HttpResponse]:
        raise NotImplementedError()
