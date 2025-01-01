from collections.abc import Awaitable, Callable

from asgikit.requests import Request

__all__ = ("CallNext",)

type CallNext = Callable[[Request], Awaitable]
