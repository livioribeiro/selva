from typing import Protocol, Type, runtime_checkable

from asgikit.requests import Request
from asgikit.responses import Response

from selva.di.decorator import service


@runtime_checkable
class ExceptionHandler[TExc: BaseException](Protocol[TExc]):
    async def handle_exception(self, request: Request, response: Response, exc: TExc):
        raise NotImplementedError()


def exception_handler(exc: Type[Exception]):
    def inner(cls):
        assert issubclass(cls, ExceptionHandler)
        return service(cls, provides=ExceptionHandler[exc])

    return inner
