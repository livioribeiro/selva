import warnings

from ward import test, raises

from dependency_injector import Container, Scope
from dependency_injector.errors import (
    FactoryMissingReturnTypeError,
    MissingDependentContextError,
    ServiceAlreadyRegisteredError,
)

from .fixtures import ioc
from .utils import Context


class Service1:
    pass


async def service1_factory() -> Service1:
    return Service1()


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


async def service2_factory(service1: Service1) -> Service2:
    return Service2(service1)


class Service3:
    pass


async def service3_factory() -> Service3:
    return Service3()


class Interface:
    pass


class Implementation(Interface):
    pass


async def interface_factory() -> Interface:
    return Implementation()


@test("has service")
def _(ioc: Container = ioc):
    ioc.register(service1_factory, Scope.SINGLETON)
    assert ioc.has(Service1)


@test("has service with scope")
def _(ioc: Container = ioc):
    ioc.register(service1_factory, Scope.SINGLETON)
    ioc.register(service2_factory, Scope.DEPENDENT)
    ioc.register(service3_factory, Scope.TRANSIENT)

    assert ioc.has(Service1, Scope.SINGLETON)
    assert ioc.has(Service2, Scope.DEPENDENT)
    assert ioc.has(Service3, Scope.TRANSIENT)


@test("service with provided interface")
async def _(ioc: Container = ioc):
    ioc.register(interface_factory, Scope.SINGLETON)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


@test("inject singleton")
async def _(ioc: Container = ioc):
    ioc.register(service1_factory, Scope.SINGLETON)
    ioc.register(service2_factory, Scope.SINGLETON)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert isinstance(service.service1, Service1)

    other_service = await ioc.get(Service2)
    assert other_service is service
    assert other_service.service1 is service.service1


@test("inject transient")
async def _(ioc: Container = ioc):
    ioc.register(service1_factory, Scope.TRANSIENT)
    ioc.register(service2_factory, Scope.TRANSIENT)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert type(service.service1) == Service1

    other_service = await ioc.get(Service2)
    assert other_service is not service
    assert other_service.service1 is not service.service1


@test("inject dependent")
async def _(ioc: Container = ioc):
    ioc.register(service1_factory, Scope.DEPENDENT)
    ioc.register(service2_factory, Scope.DEPENDENT)

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
    ioc.register(service1_factory, Scope.DEPENDENT)

    with raises(MissingDependentContextError):
        await ioc.get(Service1)


@test("interface implementation")
async def _(ioc: Container = ioc):
    ioc.register(interface_factory, Scope.SINGLETON)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


@test("factory function without return type should fail")
def _(ioc: Container = ioc):
    async def service_factory():
        return Service1()

    with raises(FactoryMissingReturnTypeError):
        ioc.register(service_factory, Scope.SINGLETON)


@test("provides option should raise warning")
def _(ioc: Container = ioc):
    with warnings.catch_warnings(record=True) as w:
        ioc.register(interface_factory, Scope.SINGLETON, provides=Interface)
        assert "option 'provides' on a factory function has no effect" == str(
            w[0].message
        )


@test("sync factory")
async def _(ioc: Container = ioc):
    def sync_factory() -> Service1:
        return Service1()

    ioc.register(sync_factory, Scope.SINGLETON)

    service = await ioc.get(Service1)
    assert isinstance(service, Service1)


@test("register a service twice should fail")
async def _(ioc: Container = ioc):
    async def duplicate_factory() -> Service1:
        return Service1()

    with raises(ServiceAlreadyRegisteredError):
        ioc.register(service1_factory, Scope.SINGLETON)
        ioc.register(duplicate_factory, Scope.SINGLETON)
