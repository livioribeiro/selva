from typing import Annotated, Generic, TypeVar

import pytest

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import TypeVarInGenericServiceError
from selva.di.inject import Inject

T = TypeVar("T")


class GenericService(Generic[T]):
    pass


@service(provides=GenericService[int])
class Service(GenericService[int]):
    pass


@service
def service_factory() -> GenericService[int]:
    return Service()


@service
class ServiceDepends:
    service: Annotated[GenericService[int], Inject]


@service
def service_factory_depends(dependency: GenericService[int]) -> ServiceDepends:
    instance = ServiceDepends()
    setattr(instance, "service", dependency)
    return instance


async def test_get_generic_service_with_class(ioc: Container):
    ioc.register(Service)

    instance = await ioc.get(GenericService[int])
    assert isinstance(instance, Service)


async def test_get_generic_service_with_factory(ioc: Container):
    ioc.register(service_factory)

    instance = await ioc.get(GenericService[int])
    assert isinstance(instance, Service)


async def test_get_generic_service_with_class_with_dependency(ioc: Container):
    ioc.register(Service)
    ioc.register(ServiceDepends)

    instance = await ioc.get(ServiceDepends)
    assert isinstance(instance, ServiceDepends)
    assert isinstance(instance.service, Service)


async def test_get_generic_service_with_factory_with_dependency(ioc: Container):
    ioc.register(service_factory)
    ioc.register(service_factory_depends)

    instance = await ioc.get(ServiceDepends)
    assert isinstance(instance, ServiceDepends)
    assert isinstance(instance.service, Service)


async def test_type_var_in_generic_service_should_fail(ioc: Container):
    with pytest.raises(TypeVarInGenericServiceError):
        ioc.register(service(Service, provides=GenericService[T]))
