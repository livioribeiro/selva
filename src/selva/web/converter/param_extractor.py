from typing import Protocol, Type, TypeVar, runtime_checkable

from asgikit.requests import Request

T = TypeVar("T")


@runtime_checkable
class ParamExtractor(Protocol[T]):
    def extract(self, request: Request, parameter_name: str, metadata: T | Type[T]):
        raise NotImplementedError()
