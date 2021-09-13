import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import Executor, ThreadPoolExecutor
from types import ModuleType
from typing import Any, Union

from .container import Container
from .service.model import InjectableType, Scope


class SyncContainer(Container):
    def __init__(self, loop: AbstractEventLoop = None, executor: Executor = None):
        executor = executor or ThreadPoolExecutor()
        self.loop = loop or asyncio.new_event_loop()
        super().__init__(loop=loop, executor=executor)

    def register(
        self,
        service: InjectableType,
        scope: Scope,
        *,
        provides: type = None,
        name: str = None
    ):
        super().register(service, scope, provides=provides, name=name)

    def scan(self, *packages: Union[str, ModuleType]):
        return super().scan(*packages)

    def has(self, service_type: type, scope: Scope = None) -> bool:
        return super().has(service_type, scope)

    def get(self, service_type: type, *, context: Any = None, name: str = None) -> Any:
        return self.loop.run_until_complete(
            super().get(service_type, context=context, name=name)
        )

    def create(self, service: type, *, context: Any = None) -> Any:
        return self.loop.run_until_complete(super().create(service, context=context))

    def call(self, *args, **kwargs) -> Any:
        return self.loop.run_until_complete(super().call(*args, **kwargs))
