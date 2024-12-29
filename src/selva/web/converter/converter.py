from collections.abc import Awaitable
from typing import Protocol, runtime_checkable

__all__ = ("Converter",)


@runtime_checkable
class Converter[TFrom, TInto](Protocol):
    def convert(self, data: TFrom, original_type: type) -> TInto | Awaitable[TInto]:
        raise NotImplementedError()
