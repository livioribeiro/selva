from typing import Protocol, TypeVar

from selva.web.context import RequestContext

T = TypeVar("T")


class RequestParamExtractor(Protocol[T]):
    def extract(self, context: RequestContext, parameter_name: str, metadata: T):
        raise NotImplementedError()
