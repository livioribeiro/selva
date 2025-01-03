from collections.abc import Awaitable
from typing import Protocol, TypeVar, runtime_checkable

__all__ = ("Converter",)


TFrom = TypeVar("TFrom")
TInto = TypeVar("TInto")


@runtime_checkable
class Converter(Protocol[TFrom, TInto]):
    def convert(self, data: TFrom, original_type: type) -> TInto | Awaitable[TInto]:
        raise NotImplementedError()
