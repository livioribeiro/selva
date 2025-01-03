from collections.abc import Awaitable, Callable
from typing import TypeAlias

from asgikit.requests import Request

__all__ = ("CallNext",)

CallNext: TypeAlias = Callable[[Request], Awaitable]
