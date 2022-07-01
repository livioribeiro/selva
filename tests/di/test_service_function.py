import pytest

from selva.di import Container, Scope
from selva.di.errors import (
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


def test_has_service(ioc: Container):
    ioc.register(service1_factory, Scope.SINGLETON)
    assert ioc.has(Service1)


def test_has_service_with_scope(ioc: Container):
    ioc.register(service1_factory, Scope.SINGLETON)
    ioc.register(service2_factory, Scope.DEPENDENT)
    ioc.register(service3_factory, Scope.TRANSIENT)

    assert ioc.has(Service1, Scope.SINGLETON)
    assert ioc.has(Service2, Scope.DEPENDENT)
    assert ioc.has(Service3, Scope.TRANSIENT)


async def test_service_with_provided_interface(ioc: Container):
    ioc.register(interface_factory, Scope.SINGLETON)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


async def test_inject_singleton(ioc: Container):
    ioc.register(service1_factory, Scope.SINGLETON)
    ioc.register(service2_factory, Scope.SINGLETON)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert isinstance(service.service1, Service1)

    other_service = await ioc.get(Service2)
    assert other_service is service
    assert other_service.service1 is service.service1


async def test_inject_transient(ioc: Container):
    ioc.register(service1_factory, Scope.TRANSIENT)
    ioc.register(service2_factory, Scope.TRANSIENT)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert type(service.service1) == Service1

    other_service = await ioc.get(Service2)
    assert other_service is not service
    assert other_service.service1 is not service.service1


async def test_inject_dependent(ioc: Container):
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


async def test_dependent_scope_without_context_should_fail(ioc: Container):
    ioc.register(service1_factory, Scope.DEPENDENT)

    with pytest.raises(MissingDependentContextError):
        await ioc.get(Service1)


async def test_interface_implementation(ioc: Container):
    ioc.register(interface_factory, Scope.SINGLETON)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


def test_factory_function_without_return_type_should_fail(ioc: Container):
    async def service_factory():
        pass

    with pytest.raises(FactoryMissingReturnTypeError):
        ioc.register(service_factory, Scope.SINGLETON)


def test_provides_option_should_raise_warning(ioc: Container):
    with pytest.warns(UserWarning):
        ioc.register(interface_factory, Scope.SINGLETON, provides=Interface)


async def test_sync_factory(ioc: Container):
    def sync_factory() -> Service1:
        return Service1()

    ioc.register(sync_factory, Scope.SINGLETON)

    service = await ioc.get(Service1)
    assert isinstance(service, Service1)


async def test_register_a_service_twice_should_fail(ioc: Container):
    async def duplicate_factory() -> Service1:
        pass

    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(service1_factory, Scope.SINGLETON)
        ioc.register(duplicate_factory, Scope.SINGLETON)
