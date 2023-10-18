from typing import Type, TypeVar, Protocol, runtime_checkable

from asgikit.requests import Request
from asgikit.responses import Response

from selva.di.decorator import service


TExc = TypeVar("TExc")


@runtime_checkable
class ExceptionHandler(Protocol[TExc]):
    async def handle_exception(self, request: Request, response: Response, exc: TExc):
        raise NotImplementedError()


def exception_handler(exc: Type[Exception]):
    def inner(cls):
        return service(cls, provides=ExceptionHandler[exc])

    return inner
