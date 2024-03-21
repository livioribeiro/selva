from typing import Annotated

import pytest

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import ServiceAlreadyRegisteredError
from selva.di.inject import Inject


@service
class Service1:
    pass


@service
class Service2:
    service1: Annotated[Service1, Inject]


@service
class Service3:
    pass


class Interface:
    pass


@service(provides=Interface)
class Implementation(Interface):
    pass


def test_has_service(ioc: Container):
    ioc.register(Service1)
    assert ioc.has(Service1)


async def test_service_with_provided_interface(ioc: Container):
    ioc.register(Implementation)

    instance = await ioc.get(Interface)
    assert isinstance(instance, Implementation)


async def test_inject_singleton(ioc: Container):
    ioc.register(Service1)
    ioc.register(Service2)

    instance = await ioc.get(Service2)
    assert isinstance(instance, Service2)
    assert isinstance(instance.service1, Service1)

    other_instance = await ioc.get(Service2)
    assert other_instance is instance
    assert other_instance.service1 is instance.service1


async def test_interface_and_implementation(ioc: Container):
    ioc.register(Implementation)

    instance = await ioc.get(Interface)
    assert isinstance(instance, Implementation)


async def test_register_a_service_twice_should_fail(ioc: Container):
    @service(provides=Interface)
    class Implementation2(Interface):
        pass

    ioc.register(Implementation)
    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(Implementation2)
