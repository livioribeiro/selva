from collections.abc import Awaitable, Callable
from typing import NamedTuple, TypeAlias, TypeVar

from asgikit.requests import Request

T_ERR = TypeVar("T_ERR", bound=BaseException)

ATTRIBUTE_EXCEPTION_HANDLER = "__selva_exception_handler__"

ExceptionHandlerType: TypeAlias = Callable[[Request, BaseException, ...], Awaitable]


class ExceptionHandlerInfo(NamedTuple):
    exception_class: type[BaseException]


def exception_handler(exc: type[BaseException]):
    assert issubclass(exc, BaseException)

    def inner(handler: ExceptionHandlerType):
        setattr(
            handler,
            ATTRIBUTE_EXCEPTION_HANDLER,
            ExceptionHandlerInfo(exception_class=exc),
        )
        return handler

    return inner
