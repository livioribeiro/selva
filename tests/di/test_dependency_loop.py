import pytest

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import DependencyLoopError


class Service1:
    def __init__(self, service2: "Service2"):
        self.service2 = service2


@service
async def service1_factory(locator) -> Service1:
    instance = await locator.get(Service2)
    return Service1(instance)


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


@service
async def service2_factory(locator) -> Service2:
    instance = await locator.get(Service1)
    return Service2(instance)


async def test_dependency_loop_should_fail(ioc: Container):
    ioc.register(service1_factory)
    ioc.register(service2_factory)

    with pytest.raises(DependencyLoopError) as e:
        await ioc.get(Service1)
