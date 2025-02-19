from collections.abc import Awaitable, Callable
from typing import TypeAlias

from selva.web.http import Request

__all__ = ("CallNext",)

CallNext: TypeAlias = Callable[[Request], Awaitable]
