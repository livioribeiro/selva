import pytest

from selva.di.container import Container
from selva.di.error import FactoryMissingReturnTypeError, ServiceAlreadyRegisteredError

from .fixtures import ioc


class Service1:
    pass


async def service1_factory() -> Service1:
    yield Service1()
    print("Service1")


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


async def service2_factory(service1: Service1) -> Service2:
    yield Service2(service1)
    print("Service2")


class Interface:
    pass


class Implementation(Interface):
    pass


async def interface_factory() -> Interface:
    yield Implementation()
    print("Interface Implementation")


def test_has_service(ioc: Container):
    ioc.register(service1_factory)
    assert ioc.has(Service1)


async def test_service_with_provided_interface(ioc: Container, capfd):
    ioc.register(interface_factory)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)

    await ioc._run_finalizers()
    assert capfd.readouterr().out == "Interface Implementation\n"


async def test_inject_singleton(ioc: Container, capfd):
    ioc.register(service1_factory)
    ioc.register(service2_factory)

    service = await ioc.get(Service2)
    assert isinstance(service, Service2)
    assert isinstance(service.service1, Service1)

    other_service = await ioc.get(Service2)
    assert other_service is service
    assert other_service.service1 is service.service1

    await ioc._run_finalizers()
    assert capfd.readouterr().out == "Service2\nService1\n"


async def test_interface_implementation(ioc: Container, capfd):
    ioc.register(interface_factory)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)

    await ioc._run_finalizers()
    assert capfd.readouterr().out == "Interface Implementation\n"


def test_factory_function_without_return_type_should_fail(ioc: Container):
    async def service_factory():
        pass

    with pytest.raises(FactoryMissingReturnTypeError):
        ioc.register(service_factory)


def test_provides_option_should_log_warning(ioc: Container, caplog):
    ioc.register(interface_factory, provides=Interface)
    assert "option 'provides' on a factory function has no effect" in caplog.text
