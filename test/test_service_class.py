import pytest

from dependency_injector import Scope
from dependency_injector.errors import (
    IncompatibleTypesError,
    MissingDependentContextError,
    ServiceAlreadyRegisteredError,
)

from . import ioc
from .utils import Context

pytestmark = pytest.mark.asyncio


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


def test_has_service(ioc):
    ioc.register(Service1, Scope.SINGLETON)
    assert ioc.has(Service1)


def test_has_service_with_scope(ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.DEPENDENT)
    ioc.register(Service3, Scope.TRANSIENT)

    assert ioc.has(Service1, Scope.SINGLETON)
    assert ioc.has(Service2, Scope.DEPENDENT)
    assert ioc.has(Service3, Scope.TRANSIENT)


async def test_service_with_provided_interface(ioc):
    ioc.register(Implementation, Scope.SINGLETON, provides=Interface)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


async def test_inject_singleton(ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.SINGLETON)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert isinstance(service.service1, Service1)

    other_service = await ioc.get(Service2)
    assert other_service is service
    assert other_service.service1 is service.service1


async def test_inject_transient(ioc):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.TRANSIENT)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert type(service.service1) == Service1

    other_service = await ioc.get(Service2)
    assert other_service is not service
    assert other_service.service1 is not service.service1


async def test_inject_dependent(ioc):
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


async def test_dependent_without_context_should_fail(ioc):
    ioc.register(Service1, Scope.DEPENDENT)

    with pytest.raises(MissingDependentContextError):
        await ioc.get(Service1)


async def test_interface_implementation(ioc):
    ioc.register(Implementation, Scope.SINGLETON, provides=Interface)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


def test_incompatible_types_should_fail(ioc):
    class NotImplementation:
        pass

    with pytest.raises(IncompatibleTypesError):
        ioc.register(NotImplementation, Scope.SINGLETON, provides=Interface)


async def test_service_registered_twice_should_fail(ioc):
    class Implementation2(Interface):
        pass

    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(Implementation, Scope.SINGLETON, provides=Interface)
        ioc.register(Implementation2, Scope.SINGLETON, provides=Interface)
