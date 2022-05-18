import asyncio

from ward import test

from dependency_injector import Container, Scope

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


@test("call initialize")
async def _(ioc: Container = ioc):
    ioc.register(Dependency, Scope.TRANSIENT)
    ioc.register(Service, Scope.TRANSIENT)

    service = await ioc.get(Service)
    assert isinstance(service.dependency, Dependency)


@test("call async initialize")
async def _(ioc: Container = ioc):
    ioc.register(Dependency, Scope.TRANSIENT)
    ioc.register(ServiceAsyncInitialize, Scope.TRANSIENT)

    service = await ioc.get(ServiceAsyncInitialize)
    assert isinstance(service.dependency, Dependency)
