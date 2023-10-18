from typing import Protocol, Type

from asgikit.requests import Request


class RequestParamExtractor[T](Protocol[T]):
    def extract(self, request: Request, parameter_name: str, metadata: T | Type[T]):
        raise NotImplementedError()
