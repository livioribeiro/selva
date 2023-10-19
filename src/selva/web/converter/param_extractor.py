from typing import Protocol, Type, runtime_checkable

from asgikit.requests import Request


@runtime_checkable
class ParamExtractor[T](Protocol[T]):
    def extract(self, request: Request, parameter_name: str, metadata: T | Type[T]):
        raise NotImplementedError()
