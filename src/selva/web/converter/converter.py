from collections.abc import Awaitable
from typing import Protocol, TypeVar, runtime_checkable

__all__ = ("Converter",)


T_FROM = TypeVar("T_FROM")
T_INTO = TypeVar("T_INTO")


@runtime_checkable
class Converter(Protocol[T_FROM, T_INTO]):
    def convert(self, data: T_FROM, original_type: type) -> T_INTO | Awaitable[T_INTO]:
        pass
