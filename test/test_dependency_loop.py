from __future__ import annotations

import pytest

from dependency_injector import Lazy, Scope
from dependency_injector.errors import DependencyLoopError

from . import ioc

pytestmark = pytest.mark.asyncio


class Service1:
    def __init__(self, service2: Service2):
        pass


class Service2:
    def __init__(self, service1: Service1):
        pass


class LazyService:
    def __init__(self, service: ServiceWithLazyDependency):
        self.service = service


class ServiceWithLazyDependency:
    def __init__(self, service: Lazy[LazyService]):
        self.service = service


async def test_dependency_loop_should_fail(ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(DependencyLoopError):
        await ioc.get(Service2)


async def test_break_dependency_loop_with_lazy(ioc):
    ioc.register(LazyService, Scope.SINGLETON)
    ioc.register(ServiceWithLazyDependency, Scope.SINGLETON)

    result = await ioc.get(LazyService)
    dependent = await result.service.service.get()
    assert isinstance(result.service, ServiceWithLazyDependency)
    assert isinstance(dependent, LazyService)
