from collections.abc import Awaitable

from selva.di.error import DependencyLoopError
from selva.di.lazy import Lazy


class Locator:
    def __init__(self, container):
        self.container = container

    async def get[T](self, service: type[T], name: str | None = None, *, optional=False, stack=None) -> T:
        return await self.container.get(service, name, optional=optional, locator=self, stack=stack or [])

    def lazy[T](self, service: type[T], name: str | None = None, optional=False) -> Lazy[T]:
        return Lazy(self.container, service, name, optional=optional)
