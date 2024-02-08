from typing import Annotated

from selva.di.container import Container
from selva.di.inject import Inject


class Service1:
    service2: Annotated["Service2", Inject]


class Service2:
    service1: Annotated[Service1, Inject]


async def test_dependency_loop(ioc: Container):
    ioc.register(Service1)
    ioc.register(Service2)

    service1 = await ioc.get(Service1)
    service2 = await ioc.get(Service2)

    assert service1 is service2.service1
    assert service2 is service1.service2
