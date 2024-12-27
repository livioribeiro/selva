from typing import Protocol, TypeVar, runtime_checkable

from asgikit.requests import Request

TExc = TypeVar("TExc", bound=BaseException)


@runtime_checkable
class ExceptionHandler(Protocol[TExc]):
    async def __call__(self, request: Request, exc: TExc):
        raise NotImplementedError()
