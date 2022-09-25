from selva.di import Container, service, initializer

from .fixtures import ioc


@service
class Service1:
    pass


@service
class Service2:
    def __init__(self, dep1: Service1):
        self.dep1 = dep1


@service
class Service3:
    def __init__(self, dep1: Service1, dep2: Service2):
        self.dep1 = dep1
        self.dep2 = dep2


@service
class Service4:
    def __init__(self, dep1: Service1, dep2: Service2, dep3: Service3):
        self.dep1 = dep1
        self.dep2 = dep2
        self.dep3 = dep3


@service
class Service5:
    def __init__(
        self,
        dep1: Service1,
        dep2: Service2,
        dep3: Service3,
        dep4: Service4,
        dep6: "Service6",
    ):
        self.dep1 = dep1
        self.dep2 = dep2
        self.dep3 = dep3
        self.dep4 = dep4
        self.dep6 = dep6


@service
class Service6:
    def __init__(self, dep1: Service1, dep2: Service2, dep3: Service3, dep4: Service4):
        self.dep1 = dep1
        self.dep2 = dep2
        self.dep3 = dep3
        self.dep4 = dep4
        self.dep5 = None

    @initializer
    def initialize(self, dep5: Service5):
        self.dep5 = dep5


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
