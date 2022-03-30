from __future__ import annotations

from ward import test, raises

from dependency_injector import Lazy, Scope
from dependency_injector.errors import DependencyLoopError

from .fixtures import ioc


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


@test("dependency_loop_should_fail")
async def _(ioc=ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.SINGLETON)

    with raises(DependencyLoopError):
        await ioc.get(Service2)


@test("break dependency loop with lazy")
async def _(ioc=ioc):
    ioc.register(LazyService, Scope.SINGLETON)
    ioc.register(ServiceWithLazyDependency, Scope.SINGLETON)

    result = await ioc.get(LazyService)
    dependent = await result.service.service.get()
    assert isinstance(result.service, ServiceWithLazyDependency)
    assert isinstance(dependent, LazyService)
