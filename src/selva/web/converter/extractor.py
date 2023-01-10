from abc import ABCMeta, abstractmethod
from collections.abc import Awaitable
from typing import Any, Generic, TypeVar, NamedTuple

from selva.di.decorator import service
from selva.web.context import RequestContext

__all__ = ("Extractor", "ExtractorArgs")

TExtractor = TypeVar("TExtractor")


class ExtractorArgs(NamedTuple, Generic[TExtractor]):
    arg_name: str
    arg_type: type
    arg_value: TExtractor


class Extractor(Generic[TExtractor], metaclass=ABCMeta):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        service(provides=cls.__orig_bases__[0])(cls)

    @abstractmethod
    def extract(self, context: RequestContext, args: ExtractorArgs[TExtractor]) -> Any | Awaitable[Any]:
        pass
