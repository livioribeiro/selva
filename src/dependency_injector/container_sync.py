import asyncio
from asyncio import AbstractEventLoop
from types import ModuleType
from typing import Any, Union

from dependency_injector.container import Container
from dependency_injector.service import InjectableType, Scope


class SyncContainer:
    def __init__(self, loop: AbstractEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()
        self.container = Container(loop=self.loop)

    def register(self, service: InjectableType, scope: Scope, *, provides: type = None):
        self.container.register(service, scope, provides=provides)

    def scan(self, *packages: Union[str, ModuleType]):
        return self.container.scan(*packages)

    def has(self, service_type: type, scope: Scope = None) -> bool:
        return self.container.has(service_type, scope)

    def get(self, service_type: type, *, context: Any = None) -> Any:
        return self.loop.run_until_complete(
            self.container.get(service_type, context=context)
        )

    def call(self, *args, **kwargs) -> Any:
        return self.loop.run_until_complete(self.container.call(*args, **kwargs))
