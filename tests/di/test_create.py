from typing import Annotated

from selva.di.container import Container
from selva.di.inject import Inject


class Service1:
    pass


def service1_factory() -> Service1:
    return Service1()


class Service2:
    service1: Annotated[Service1, Inject]


def service2_factory(service1: Service1) -> Service2:
    service = Service2()
    setattr(service, "service1", service1)
    return service


class Creatable:
    service2: Annotated[Service2, Inject]


async def test_create_object_with_class(ioc: Container):
    ioc.register(Service1)
    ioc.register(Service2)

    result = await ioc.create(Creatable)

    assert isinstance(result.service2, Service2)
    assert isinstance(result.service2.service1, Service1)


async def test_create_object_with_factory(ioc: Container):
    ioc.register(service1_factory)
    ioc.register(service2_factory)

    result = await ioc.create(Creatable)

    assert isinstance(result.service2, Service2)
    assert isinstance(result.service2.service1, Service1)
