from typing import Generic, TypeVar

import pytest

from dependency_injector import Scope
from dependency_injector.errors import (
    IncompatibleTypesError,
    TypeVarInGenericServiceError,
)

from . import ioc

pytestmark = pytest.mark.asyncio

T = TypeVar("T")


class GenericService(Generic[T]):
    pass


class Service(GenericService[int]):
    pass


def service_factory() -> GenericService[int]:
    return Service()


class ServiceDepends:
    def __init__(self, service: GenericService[int]):
        self.service = service


def service_factory_depends(service: GenericService[int]) -> ServiceDepends:
    return ServiceDepends(service)


async def test_get_generic_service_class(ioc):
    ioc.register(Service, Scope.SINGLETON, provides=GenericService[int])

    service = await ioc.get(GenericService[int])
    assert isinstance(service, Service)


async def test_get_generic_service_factory(ioc):
    ioc.register(service_factory, Scope.SINGLETON)

    service = await ioc.get(GenericService[int])
    assert isinstance(service, Service)


async def test_get_generic_service_class_with_dependency(ioc):
    ioc.register(Service, Scope.SINGLETON, provides=GenericService[int])
    ioc.register(ServiceDepends, Scope.SINGLETON)

    service = await ioc.get(ServiceDepends)
    assert isinstance(service, ServiceDepends)
    assert isinstance(service.service, Service)


async def test_get_generic_service_factory_with_dependency(ioc):
    ioc.register(service_factory, Scope.SINGLETON)
    ioc.register(service_factory_depends, Scope.SINGLETON)

    service = await ioc.get(ServiceDepends)
    assert isinstance(service, ServiceDepends)
    assert isinstance(service.service, Service)


async def test_service_provides_wrong_generic_type_should_fail(ioc):
    U = TypeVar("U")

    class AnotherGenericService(Generic[U]):
        pass

    with pytest.raises(IncompatibleTypesError):
        ioc.register(Service, Scope.SINGLETON, provides=AnotherGenericService[int])


async def test_service_provides_wrong_generic_parameter_should_fail(ioc):
    with pytest.raises(IncompatibleTypesError):
        ioc.register(Service, Scope.SINGLETON, provides=GenericService[str])


async def test_type_var_in_generic_service_should_fail(ioc):
    with pytest.raises(TypeVarInGenericServiceError):
        ioc.register(Service, Scope.SINGLETON, provides=GenericService[T])
