from collections.abc import Awaitable
from typing import Generic, Protocol, TypeVar

from asgikit.responses import HttpResponse

__all__ = ("IntoResponse",)

T = TypeVar("T")


class IntoResponse(Generic[T]):
    def into_response(self, value: T) -> HttpResponse | Awaitable[HttpResponse]:
        pass


def get_base_types(obj: object) -> list[type | Generic]:
    base_class = type(obj)
    result = list(base_class.__mro__)

    # remove 'object' type
    result.pop()

    if Generic in result:
        if Protocol in result:
            index = result.index(Protocol)
        else:
            index = result.index(Generic)

        result = result[:index]
        result.extend(base_class.__orig_bases__)

    return result
