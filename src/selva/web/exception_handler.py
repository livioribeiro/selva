from typing import Protocol, Type, TypeVar, runtime_checkable

from asgikit.requests import Request

from selva.di.decorator import service

TExc = TypeVar("TExc", bound=BaseException)


@runtime_checkable
class ExceptionHandler(Protocol[TExc]):
    async def handle_exception(self, request: Request, exc: TExc):
        raise NotImplementedError()


def exception_handler(exc: Type[BaseException]):
    def inner(cls):
        assert issubclass(cls, ExceptionHandler)
        return service(cls, provides=ExceptionHandler[exc])

    return inner
