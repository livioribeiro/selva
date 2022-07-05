from typing import Generic, TypeVar

import pytest

from selva.di import Container
from selva.di.errors import IncompatibleTypesError, TypeVarInGenericServiceError

from .fixtures import ioc

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


async def test_get_generic_service_with_class(ioc: Container):
    ioc.register(Service, provides=GenericService[int])

    service = await ioc.get(GenericService[int])
    assert isinstance(service, Service)


async def test_get_generic_service_with_factory(ioc: Container):
    ioc.register(service_factory)

    service = await ioc.get(GenericService[int])
    assert isinstance(service, Service)


async def test_get_generic_service_with_class_with_dependency(ioc: Container):
    ioc.register(Service,provides=GenericService[int])
    ioc.register(ServiceDepends)

    service = await ioc.get(ServiceDepends)
    assert isinstance(service, ServiceDepends)
    assert isinstance(service.service, Service)


async def test_get_generic_service_with_factory_with_dependency(ioc: Container):
    ioc.register(service_factory)
    ioc.register(service_factory_depends)

    service = await ioc.get(ServiceDepends)
    assert isinstance(service, ServiceDepends)
    assert isinstance(service.service, Service)


async def test_service_registered_with_wrong_generic_type_should_fail(ioc: Container):
    U = TypeVar("U")

    class AnotherGenericService(Generic[U]):
        pass

    with pytest.raises(IncompatibleTypesError):
        ioc.register(Service, provides=AnotherGenericService[int])


async def test_service_provides_wrong_generic_parameter_should_fail(ioc: Container):
    with pytest.raises(IncompatibleTypesError):
        ioc.register(Service,provides=GenericService[str])


async def test_type_var_in_generic_service_should_fail(ioc: Container):
    with pytest.raises(TypeVarInGenericServiceError):
        ioc.register(Service, provides=GenericService[T])
