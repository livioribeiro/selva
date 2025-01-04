import asyncio
from typing import Annotated

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.inject import Inject


@service
class Service1:
    pass


@service
class Service2:
    dep1: Annotated[Service1, Inject]


@service
class Service3:
    dep1: Annotated[Service1, Inject]
    dep2: Annotated[Service2, Inject]


@service
class Service4:
    dep1: Annotated[Service1, Inject]
    dep2: Annotated[Service2, Inject]
    dep3: Annotated[Service3, Inject]


@service
class Service5:
    dep1: Annotated[Service1, Inject]
    dep2: Annotated[Service2, Inject]
    dep3: Annotated[Service3, Inject]
    dep4: Annotated[Service4, Inject]
    dep6: Annotated["Service6", Inject]


@service
class Service6:
    dep1: Annotated[Service1, Inject]
    dep2: Annotated[Service2, Inject]
    dep3: Annotated[Service3, Inject]
    dep4: Annotated[Service4, Inject]
    dep5: Annotated[Service5, Inject]


async def test_get_service(ioc: Container):
    for svc in [Service1, Service2, Service3, Service4]:
        ioc.register(svc)

    instance = await ioc.get(Service4)
    assert isinstance(instance, Service4)


async def test_dependency_loop(ioc: Container):
    for svc in [Service1, Service2, Service3, Service4, Service5, Service6]:
        ioc.register(svc)

    instance5 = await ioc.get(Service5)
    instance6 = await ioc.get(Service6)

    assert isinstance(instance5, Service5)
    assert isinstance(instance6, Service6)

    assert instance5.dep6 is instance6
    assert instance6.dep5 is instance5


async def test_get_simultaneously(ioc: Container):
    for svc in [Service1, Service2, Service3, Service4, Service5, Service6]:
        ioc.register(svc)

    (
        instance1,
        instance2,
        instance3,
        instance4,
        instance5,
        instance6,
    ) = await asyncio.gather(
        ioc.get(Service1),
        ioc.get(Service2),
        ioc.get(Service3),
        ioc.get(Service4),
        ioc.get(Service5),
        ioc.get(Service6),
    )

    assert isinstance(instance1, Service1)
    assert isinstance(instance2, Service2)
    assert isinstance(instance3, Service3)
    assert isinstance(instance4, Service4)
    assert isinstance(instance5, Service5)
    assert isinstance(instance6, Service6)

    assert instance5.dep6 is instance6
    assert instance6.dep5 is instance5
