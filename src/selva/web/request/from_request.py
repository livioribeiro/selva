from typing import Generic, TypeVar

from .context import RequestContext

__all__ = ("FromRequest",)

T = TypeVar("T")


class FromRequest(Generic[T]):
    async def from_request(self, context: RequestContext) -> T:
        pass
