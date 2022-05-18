from typing import Generic, TypeVar

from ward import test, raises

from dependency_injector import Container, Scope
from dependency_injector.errors import (
    IncompatibleTypesError,
    TypeVarInGenericServiceError,
)

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


@test("get generic service with class")
async def _(ioc: Container = ioc):
    ioc.register(Service, Scope.SINGLETON, provides=GenericService[int])

    service = await ioc.get(GenericService[int])
    assert isinstance(service, Service)


@test("get generic service with factory")
async def _(ioc: Container = ioc):
    ioc.register(service_factory, Scope.SINGLETON)

    service = await ioc.get(GenericService[int])
    assert isinstance(service, Service)


@test("get generic service with class with dependency")
async def _(ioc: Container = ioc):
    ioc.register(Service, Scope.SINGLETON, provides=GenericService[int])
    ioc.register(ServiceDepends, Scope.SINGLETON)

    service = await ioc.get(ServiceDepends)
    assert isinstance(service, ServiceDepends)
    assert isinstance(service.service, Service)


@test("get generic service with factory with dependency")
async def _(ioc: Container = ioc):
    ioc.register(service_factory, Scope.SINGLETON)
    ioc.register(service_factory_depends, Scope.SINGLETON)

    service = await ioc.get(ServiceDepends)
    assert isinstance(service, ServiceDepends)
    assert isinstance(service.service, Service)


@test("service registered with wrong generic type should fail")
async def _(ioc: Container = ioc):
    U = TypeVar("U")

    class AnotherGenericService(Generic[U]):
        pass

    with raises(IncompatibleTypesError):
        ioc.register(Service, Scope.SINGLETON, provides=AnotherGenericService[int])


@test("service provides wrong generic parameter should fail")
async def _(ioc: Container = ioc):
    with raises(IncompatibleTypesError):
        ioc.register(Service, Scope.SINGLETON, provides=GenericService[str])


@test("type var in generic service should fail")
async def _(ioc: Container = ioc):
    with raises(TypeVarInGenericServiceError):
        ioc.register(Service, Scope.SINGLETON, provides=GenericService[T])
