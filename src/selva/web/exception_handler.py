from collections.abc import Awaitable, Callable
from typing import NamedTuple, Type, TypeVar

from asgikit.requests import Request

TExc = TypeVar("TExc", bound=BaseException)

ATTRIBUTE_EXCEPTION_HANDLER = "__selva_exception_handler__"

ExceptionHandlerType = Callable[[Request, BaseException, ...], Awaitable]


class ExceptionHandlerInfo(NamedTuple):
    exception_class: Type[BaseException]


def exception_handler(exc: Type[BaseException]):
    assert issubclass(exc, BaseException)

    def inner(handler: ExceptionHandlerType):
        setattr(handler, ATTRIBUTE_EXCEPTION_HANDLER, ExceptionHandlerInfo(exception_class=exc))
        return handler

    return inner
