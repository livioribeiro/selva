from selva.di import Container, Scope

from .fixtures import ioc


class Dependency:
    pass


class Service:
    def __init__(self):
        self.dependency = None

    def initialize(self, dependency: Dependency):
        self.dependency = dependency


class ServiceAsyncInitialize:
    def __init__(self):
        self.dependency = None

    async def initialize(self, dependency: Dependency):
        self.dependency = dependency


async def test_call_initialize(ioc: Container):
    ioc.register(Dependency, Scope.TRANSIENT)
    ioc.register(Service, Scope.TRANSIENT)

    service = await ioc.get(Service)
    assert isinstance(service.dependency, Dependency)


async def test_call_async_initialize(ioc: Container):
    ioc.register(Dependency, Scope.TRANSIENT)
    ioc.register(ServiceAsyncInitialize, Scope.TRANSIENT)

    service = await ioc.get(ServiceAsyncInitialize)
    assert isinstance(service.dependency, Dependency)
