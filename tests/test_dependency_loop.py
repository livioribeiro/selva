from ward import raises, test

from dependency_injector import Container, Scope
from dependency_injector.errors import DependencyLoopError

from .fixtures import ioc


class Service1:
    def __init__(self, service2: "Service2"):
        pass


class Service2:
    def __init__(self, service1: Service1):
        pass


class LazyService:
    def __init__(self, service: "ServiceWithLazyDependency"):
        self.service = service


class ServiceWithLazyDependency:
    def __init__(self):
        self.lazy = None

    def initialize(self, service: LazyService):
        self.lazy = service


@test("dependency loop should fail")
async def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.SINGLETON)

    with raises(DependencyLoopError):
        await ioc.get(Service2)


@test("break dependency loop with initialize method")
async def _(ioc: Container = ioc):
    ioc.register(LazyService, Scope.SINGLETON)
    ioc.register(ServiceWithLazyDependency, Scope.SINGLETON)

    result = await ioc.get(ServiceWithLazyDependency)
    assert isinstance(result.lazy, LazyService)
