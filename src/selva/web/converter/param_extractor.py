from abc import ABC
from typing import Protocol, Type, runtime_checkable

from asgikit.requests import Request


@runtime_checkable
class ParamExtractor[T](Protocol):
    def extract(
        self,
        request: Request,
        parameter_name: str,
        metadata: T | Type[T]
    ):
        raise NotImplementedError()


class FromBody:
    pass


class FromRequestParam(ABC):
    def __init__(self, name: str = None):
        self.name = name


class FromPath(FromRequestParam):
    pass


class FromQuery(FromRequestParam):
    pass


class FromHeader(FromRequestParam):
    pass


class FromCookie(FromRequestParam):
    pass
