from dataclasses import dataclass

from ward import test, raises

from dependency_injector import Container, Scope
from dependency_injector.errors import (
    IncompatibleTypesError,
    MissingDependentContextError,
    ServiceAlreadyRegisteredError,
)

from .fixtures import ioc
from .utils import Context


class Service1:
    pass


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


class Service3:
    pass


class Interface:
    pass


class Implementation(Interface):
    pass


@dataclass
class ServiceDataClass:
    service1: Service1


@test("has service")
def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.SINGLETON)
    assert ioc.has(Service1)


@test("has service with scope")
def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.DEPENDENT)
    ioc.register(Service3, Scope.TRANSIENT)

    assert ioc.has(Service1, Scope.SINGLETON)
    assert ioc.has(Service2, Scope.DEPENDENT)
    assert ioc.has(Service3, Scope.TRANSIENT)


@test("service with provided interface")
async def _(ioc: Container = ioc):
    ioc.register(Implementation, Scope.SINGLETON, provides=Interface)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


@test("inject singleton")
async def test_inject_singleton(ioc: Container = ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.SINGLETON)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert isinstance(service.service1, Service1)

    other_service = await ioc.get(Service2)
    assert other_service is service
    assert other_service.service1 is service.service1


@test("inject transient")
async def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.TRANSIENT)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert type(service.service1) == Service1

    other_service = await ioc.get(Service2)
    assert other_service is not service
    assert other_service.service1 is not service.service1


@test("inject dependent")
async def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.DEPENDENT)
    ioc.register(Service2, Scope.DEPENDENT)

    context = Context()

    service = await ioc.get(Service2, context=context)
    assert isinstance(service, Service2)
    assert type(service.service1) == Service1

    other_service = await ioc.get(Service2, context=context)
    assert other_service is service
    assert other_service.service1 is service.service1

    context2 = Context()
    another_service = await ioc.get(Service2, context=context2)
    assert another_service is not service
    assert another_service.service1 is not service.service1


@test("dependent scope without context should fail")
async def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.DEPENDENT)

    with raises(MissingDependentContextError):
        await ioc.get(Service1)


@test("interface and implementation")
async def _(ioc: Container = ioc):
    ioc.register(Implementation, Scope.SINGLETON, provides=Interface)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


@test("incompatible types should fail")
def _(ioc: Container = ioc):
    class NotImplementation:
        pass

    with raises(IncompatibleTypesError):
        ioc.register(NotImplementation, Scope.SINGLETON, provides=Interface)


@test("register a service twice should fail")
async def _(ioc: Container = ioc):
    class Implementation2(Interface):
        pass

    ioc.register(Implementation, Scope.SINGLETON, provides=Interface)
    with raises(ServiceAlreadyRegisteredError):
        ioc.register(Implementation2, Scope.SINGLETON, provides=Interface)


@test("service dataclass")
async def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(ServiceDataClass, Scope.SINGLETON)

    service = await ioc.get(ServiceDataClass)

    assert isinstance(service.service1, Service1)
