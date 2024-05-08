import pytest
from structlog.testing import capture_logs

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import FactoryMissingReturnTypeError, ServiceAlreadyRegisteredError


class Service1:
    pass


@service
async def service1_factory() -> Service1:
    return Service1()


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


@service
async def service2_factory(service1: Service1) -> Service2:
    return Service2(service1)


class Interface:
    pass


class Implementation(Interface):
    pass


@service
async def interface_factory() -> Interface:
    return Implementation()


def test_has_service(ioc: Container):
    ioc.register(service1_factory)
    assert ioc.has(Service1)


async def test_service_with_provided_interface(ioc: Container):
    ioc.register(interface_factory)

    instance = await ioc.get(Interface)
    assert isinstance(instance, Implementation)


async def test_inject_singleton(ioc: Container):
    ioc.register(service1_factory)
    ioc.register(service2_factory)

    instance = await ioc.get(Service2)
    assert isinstance(instance, Service2)
    assert isinstance(instance.service1, Service1)

    other_instance = await ioc.get(Service2)
    assert other_instance is instance
    assert other_instance.service1 is instance.service1


async def test_interface_implementation(ioc: Container):
    ioc.register(interface_factory)

    instance = await ioc.get(Interface)
    assert isinstance(instance, Implementation)


def test_factory_function_without_return_type_should_fail(ioc: Container):
    @service
    async def service_factory():
        pass

    with pytest.raises(FactoryMissingReturnTypeError):
        ioc.register(service_factory)


def test_provides_option_should_log_warning(ioc: Container):
    @service(provides=Interface)
    async def factory() -> Interface:
        pass

    with capture_logs() as cap_logs:
        ioc.register(factory)

    assert (
        cap_logs[0]["event"] == "option 'provides' on a factory function has no effect"
    )


async def test_sync_factory(ioc: Container):
    @service
    def sync_factory() -> Service1:
        return Service1()

    ioc.register(sync_factory)

    instance = await ioc.get(Service1)
    assert isinstance(instance, Service1)


async def test_register_a_service_twice_should_fail(ioc: Container):
    @service
    async def duplicate_factory() -> Service1:
        pass

    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(service1_factory)
        ioc.register(duplicate_factory)
