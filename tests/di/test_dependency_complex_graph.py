from typing import Annotated

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.inject import Inject
from selva.di.lazy import Lazy


@service
def service1_factory() -> "Service1":
    return Service1()


class Service1:
    pass


@service
async def service2_factory(locator) -> "Service2":
    service1 = await locator.get(Service1)
    return Service2(service1)


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


@service
async def service3_factory(locator) -> "Service3":
    service1 = await locator.get(Service1)
    service2 = await locator.get(Service2)
    return Service3(service1, service2)


class Service3:
    def __init__(self, service1: Service1, service2: Service2):
        self.service1 = service1
        self.service2 = service2


@service
async def service4_factory(locator) -> "Service4":
    service1 = await locator.get(Service1)
    service2 = await locator.get(Service2)
    service3 = await locator.get(Service3)
    return Service4(service1, service2, service3)


class Service4:
    def __init__(self, service1: Service1, service2: Service2, service3: Service3):
        self.service1 = service1
        self.service2 = service2
        self.service3 = service3


@service
async def service5_factory(locator) -> "Service5":
    service1 = await locator.get(Service1)
    service2 = await locator.get(Service2)
    service3 = await locator.get(Service3)
    service4 = await locator.get(Service4)
    service6 = await locator.get(Service6)
    return Service5(service1, service2, service3, service4, service6)


class Service5:
    def __init__(self, service1: Service1, service2: Service2, service3: Service3, service4: Service4, service6: "Service6"):
        self.service1 = service1
        self.service2 = service2
        self.service3 = service3
        self.service4 = service4
        self.service6 = service6


@service
async def service6_factory(locator) -> "Service6":
    service1 = await locator.get(Service1)
    service2 = await locator.get(Service2)
    service3 = await locator.get(Service3)
    service4 = await locator.get(Service4)
    service5 = locator.lazy(Service5)
    return Service6(service1, service2, service3, service4, service5)


class Service6:
    def __init__(self, service1: Service1, service2: Service2, service3: Service3, service4: Service4, service5: Lazy[Service5]):
        self.service1 = service1
        self.service2 = service2
        self.service3 = service3
        self.service4 = service4
        self.service5 = service5


async def test_complex_graph(ioc: Container):
    ioc.register(service1_factory)
    ioc.register(service2_factory)
    ioc.register(service3_factory)
    ioc.register(service4_factory)

    instance = await ioc.get(Service4)
    assert isinstance(instance, Service4)


async def test_complex_graph_with_loop(ioc: Container):
    ioc.scan("tests.di.test_dependency_complex_graph")

    service5 = await ioc.get(Service5)
    service6 = await ioc.get(Service6)

    assert isinstance(service5, Service5)
    assert isinstance(service6, Service6)

    assert service5.service6 is service6
    assert (await service6.service5()) is service5
