import pytest

from dependency_injector import Scope
from dependency_injector.errors import (
    FactoryMissingReturnTypeError,
    MissingDependentContextError,
    ServiceAlreadyRegisteredError,
)

from . import ioc
from .utils import Context

pytestmark = pytest.mark.asyncio


def test_has_service(ioc):
    from .services.service_function import has_service as module

    ioc.scan(module)

    result = ioc.has(module.Service)
    assert result


def test_has_service_with_scope(ioc):
    from .services.service_function import has_service_with_scope as module

    ioc.scan(module)

    result_transient = ioc.has(module.ServiceTransient, Scope.TRANSIENT)
    result_dependent = ioc.has(module.ServiceDependent, Scope.DEPENDENT)
    result_singleton = ioc.has(module.ServiceSingleton, Scope.SINGLETON)

    assert result_transient
    assert result_dependent
    assert result_singleton


async def test_inject_singleton(ioc):
    from .services.service_function import inject_singleton as module

    ioc.scan(module)

    service = await ioc.get(module.Service2)
    assert isinstance(service, module.Service2)
    assert isinstance(service.service1, module.Service1)

    other_service = await ioc.get(module.Service2)
    assert other_service is service
    assert other_service.service1 is service.service1


async def test_inject_transient(ioc):
    from .services.service_function import inject_transient as module

    ioc.scan(module)

    service = await ioc.get(module.Service2)
    assert isinstance(service, module.Service2)
    assert type(service.service1) == module.Service1

    other_service = await ioc.get(module.Service2)
    assert other_service is not service
    assert other_service.service1 is not service.service1


async def test_inject_dependent(ioc):
    from .services.service_function import inject_dependent as module

    ioc.scan(module)
    context = Context()

    service = await ioc.get(module.Service2, context=context)
    assert isinstance(service, module.Service2)
    assert type(service.service1) == module.Service1

    other_service = await ioc.get(module.Service2, context=context)
    assert other_service is service
    assert other_service.service1 is service.service1

    context2 = Context()
    another_service = await ioc.get(module.Service2, context=context2)
    assert another_service is not service
    assert another_service.service1 is not service.service1


async def test_dependent_without_context_should_fail(ioc):
    from .services.service_function import (
        dependent_without_context_should_fail as module,
    )

    ioc.scan(module)

    with pytest.raises(MissingDependentContextError):
        await ioc.get(module.Service)


async def test_interface_implementation(ioc):
    from .services.service_function import interface_implementation as module

    ioc.scan(module)

    service = await ioc.get(module.Interface)
    assert isinstance(service, module.Implementation)


def test_factory_function_without_return_type_should_fail(ioc):
    from .services.service_function import (
        factory_function_without_return_type_should_fail as module,
    )

    with pytest.raises(FactoryMissingReturnTypeError):
        ioc.scan(module)


def test_provides_option_should_raise_warning(ioc):
    from .services.service_function import (
        provides_option_should_raise_warning as module,
    )

    with pytest.warns(UserWarning):
        ioc.scan(module)


async def test_sync_factory(ioc):
    from .services.service_function import sync_factory as module

    ioc.scan(module)

    service = await ioc.get(module.Service)
    assert isinstance(service, module.Service)


async def test_register(ioc):
    class Service:
        pass

    def factory() -> Service:
        return Service()

    ioc.register(factory, Scope.SINGLETON)
    assert ioc.has(Service, Scope.SINGLETON)

    service = await ioc.get(Service)
    assert isinstance(service, Service)


async def test_register_with_provides(ioc):
    class Interface:
        pass

    class Implementation(Interface):
        pass

    def factory() -> Interface:
        return Implementation()

    ioc.register(factory, Scope.SINGLETON)
    assert ioc.has(Interface, Scope.SINGLETON)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)


def test_register_with_provides_option_should_raise_warning(ioc):
    class Interface:
        pass

    class Implementation(Interface):
        pass

    def factory() -> Interface:
        return Implementation()

    with pytest.warns(UserWarning):
        ioc.register(factory, Scope.SINGLETON, provides=Interface)


async def test_service_registered_twice_should_fail(ioc):
    from .services.service_function import (
        service_registered_twice_should_fail as module,
    )

    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.scan(module)
