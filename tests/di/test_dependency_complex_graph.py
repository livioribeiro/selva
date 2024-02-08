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


async def test_complex_graph(ioc: Container):
    ioc.scan("tests.di.test_dependency_complex_graph")
    service = await ioc.get(Service4)
    assert isinstance(service, Service4)


async def test_complex_graph_with_loop(ioc: Container):
    ioc.scan("tests.di.test_dependency_complex_graph")

    service5 = await ioc.get(Service5)
    service6 = await ioc.get(Service6)

    assert isinstance(service5, Service5)
    assert isinstance(service6, Service6)

    assert service5.dep6 is service6
    assert service6.dep5 is service5
