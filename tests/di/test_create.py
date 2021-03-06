from selva.di import Container

from .fixtures import ioc


class Service1:
    pass


def service1_factory() -> Service1:
    return Service1()


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


def service2_factory(service1: Service1) -> Service2:
    return Service2(service1)


class Creatable:
    def __init__(self, service2: Service2):
        self.service2 = service2


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
