from typing import Annotated, Generic, TypeVar

import pytest

from selva.di.container import Container
from selva.di.error import TypeVarInGenericServiceError
from selva.di.inject import Inject

from .fixtures import ioc

T = TypeVar("T")


class GenericService(Generic[T]):
    pass


class Service(GenericService[int]):
    pass


def service_factory() -> GenericService[int]:
    return Service()


class ServiceDepends:
    service: Annotated[GenericService[int], Inject]


def service_factory_depends(service: GenericService[int]) -> ServiceDepends:
    instance = ServiceDepends()
    setattr(instance, "service", service)
    return instance


async def test_get_generic_service_with_class(ioc: Container):
    ioc.register(Service, provides=GenericService[int])

    service = await ioc.get(GenericService[int])
    assert isinstance(service, Service)


async def test_get_generic_service_with_factory(ioc: Container):
    ioc.register(service_factory)

    service = await ioc.get(GenericService[int])
    assert isinstance(service, Service)


async def test_get_generic_service_with_class_with_dependency(ioc: Container):
    ioc.register(Service, provides=GenericService[int])
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


async def test_type_var_in_generic_service_should_fail(ioc: Container):
    with pytest.raises(TypeVarInGenericServiceError):
        ioc.register(Service, provides=GenericService[T])
