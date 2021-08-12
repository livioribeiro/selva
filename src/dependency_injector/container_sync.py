import asyncio
from typing import Any, Callable, Dict

from dependency_injector.container import Container
from dependency_injector.service import InjectableType, Scope


class SyncContainer:
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self._container = Container()
        self._loop = loop or asyncio.get_event_loop()

    def register(self, service: InjectableType, scope: Scope, *, provides: type = None):
        self._container.register(service, scope, provides=provides)

    def scan_packages(self, *packages):
        return self._container.scan_packages(*packages)

    def has(self, service_type: type, scope: Scope = None) -> bool:
        return self._container.has(service_type, scope)

    def get(self, service_type: type, *, context: Any = None) -> Any:
        return self._loop.run_until_complete(
            self._container.get(service_type, context=context)
        )

    def call(
        self,
        func: Callable,
        *,
        context: Any = None,
        kwargs: Dict[str, Any] = None,
    ) -> Any:
        return self._loop.run_until_complete(
            self._container.call(func, context=context, kwargs=kwargs)
        )
