from dataclasses import dataclass

import pytest

from selva.di import Container
from selva.di.errors import (
    IncompatibleTypesError,
    ServiceAlreadyRegisteredError,
)

from .fixtures import ioc


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


def test_has_service(ioc: Container):
    ioc.register(Service1)
    assert ioc.has(Service1)


async def test_service_with_provided_interface(ioc: Container):
    ioc.register(Implementation, provides=Interface)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


async def test_inject_singleton(ioc: Container):
    ioc.register(Service1)
    ioc.register(Service2)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert isinstance(service.service1, Service1)

    other_service = await ioc.get(Service2)
    assert other_service is service
    assert other_service.service1 is service.service1


async def test_interface_and_implementation(ioc: Container):
    ioc.register(Implementation, provides=Interface)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


def test_incompatible_types_should_fail(ioc: Container):
    class NotImplementation:
        pass

    with pytest.raises(IncompatibleTypesError):
        ioc.register(NotImplementation, provides=Interface)


async def test_register_a_service_twice_should_fail(ioc: Container):
    class Implementation2(Interface):
        pass

    ioc.register(Implementation, provides=Interface)
    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(Implementation2, provides=Interface)


async def test_service_dataclass(ioc: Container):
    ioc.register(Service1)
    ioc.register(ServiceDataClass)

    service = await ioc.get(ServiceDataClass)

    assert isinstance(service.service1, Service1)
