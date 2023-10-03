from typing import Protocol, Type, TypeVar

from asgikit.requests import Request

T = TypeVar("T")


class RequestParamExtractor(Protocol[T]):
    def extract(self, request: Request, parameter_name: str, metadata: T | Type[T]):
        raise NotImplementedError()
