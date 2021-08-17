import pytest

from dependency_injector.errors import (
    IncompatibleTypesError,
    MissingDependentContextError,
    ServiceAlreadyRegisteredError,
)
from dependency_injector.service import Scope

from ..utils import Context
from . import ioc


def test_has_service(ioc):
    from .services.service_class import has_service as module

    ioc.scan(module)
    result = ioc.has(module.Service)
    assert result


def test_has_service_with_scope(ioc):
    from .services.service_class import has_service_with_scope as module

    ioc.scan(module)

    result_transient = ioc.has(module.ServiceTransient, Scope.TRANSIENT)
    result_dependent = ioc.has(module.ServiceDependent, Scope.DEPENDENT)
    result_singleton = ioc.has(module.ServiceSingleton, Scope.SINGLETON)

    assert result_transient
    assert result_dependent
    assert result_singleton


def test_inject_singleton(ioc):
    from .services.service_class import inject_singleton as module

    ioc.scan(module)

    service = ioc.get(module.Service2)
    assert isinstance(service, module.Service2)
    assert isinstance(service.service1, module.Service1)

    other_service = ioc.get(module.Service2)
    assert other_service is service
    assert other_service.service1 is service.service1


def test_inject_transient(ioc):
    from .services.service_class import inject_transient as module

    ioc.scan(module)

    service = ioc.get(module.Service2)
    assert isinstance(service, module.Service2)
    assert type(service.service1) == module.Service1

    other_service = ioc.get(module.Service2)
    assert other_service is not service
    assert other_service.service1 is not service.service1


def test_inject_dependent(ioc):
    from .services.service_class import inject_dependent as module

    ioc.scan(module)
    context = Context()

    service = ioc.get(module.Service2, context=context)
    assert isinstance(service, module.Service2)
    assert type(service.service1) == module.Service1

    other_service = ioc.get(module.Service2, context=context)
    assert other_service is service
    assert other_service.service1 is service.service1

    context2 = Context()
    another_service = ioc.get(module.Service2, context=context2)
    assert another_service is not service
    assert another_service.service1 is not service.service1


def test_dependent_without_context_should_fail(ioc):
    from .services.service_class import dependent_without_context_should_fail as module

    ioc.scan(module)

    with pytest.raises(MissingDependentContextError):
        ioc.get(module.Service)


def test_interface_implementation(ioc):
    from .services.service_class import interface_implementation as module

    ioc.scan(module)

    service = ioc.get(module.Interface)
    assert isinstance(service, module.Implementation)


def test_incompatible_types_should_fail(ioc):
    from .services.service_class import incompatible_types_should_fail as module

    with pytest.raises(IncompatibleTypesError):
        ioc.scan(module)


def test_register(ioc):
    class Service:
        pass

    ioc.register(Service, Scope.SINGLETON)
    assert ioc.has(Service, Scope.SINGLETON)

    service = ioc.get(Service)
    assert isinstance(service, Service)


def test_register_with_provides(ioc):
    class Interface:
        pass

    class Implementation(Interface):
        pass

    ioc.register(Implementation, Scope.SINGLETON, provides=Interface)
    assert ioc.has(Interface, Scope.SINGLETON)

    service = ioc.get(Interface)
    assert isinstance(service, Implementation)


def test_service_registered_twice_should_fail(ioc):
    from .services.service_class import service_registered_twice_should_fail as module

    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.scan(module)
