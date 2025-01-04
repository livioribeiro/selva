from typing import Annotated

import pytest

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import DependencyLoopError
from selva.di.inject import Inject


@service
class Service1:
    service2: Annotated["Service2", Inject]


@service
class Service2:
    service1: Annotated[Service1, Inject]


@service
def factory1(service2: Service2) -> Service1:
    return Service1(service2)


@service
def factory2(service1: Service1) -> Service2:
    return Service2(service1)


async def test_service_class(ioc: Container):
    ioc.register(Service1)
    ioc.register(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert service1 is service2.service1
    assert service2 is service1.service2


async def test_service_factory(ioc: Container):
    ioc.register(factory1)
    ioc.register(factory2)

    with pytest.raises(DependencyLoopError):
        await ioc.get(Service1)
