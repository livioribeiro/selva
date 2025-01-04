import pytest

from selva.di.container import Container
from selva.di.decorator import service


@pytest.fixture
def service_class():
    class ServiceClass:
        startup_called = False

        def initialize(self):
            ServiceClass.startup_called = not ServiceClass.startup_called

    return ServiceClass


@pytest.fixture
def service_factory(service_class):
    def service_factory() -> service_class:
        service_class.startup_called = not service_class.startup_called
        return service_class()

    return service_factory


async def test_startup_class(ioc: Container, service_class):
    ioc.register(service(service_class, startup=True))
    await ioc.init_startup_services()
    assert service_class.startup_called


async def test_startup_factory(ioc: Container, service_class, service_factory):
    ioc.register(service(service_factory, startup=True))
    await ioc.init_startup_services()
    assert service_class.startup_called
