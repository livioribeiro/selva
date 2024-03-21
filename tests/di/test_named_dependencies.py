from typing import Annotated

import pytest

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import ServiceAlreadyRegisteredError, ServiceNotFoundError
from selva.di.inject import Inject


@service(name="1")
class DependentService:
    pass


@service
class ServiceWithNamedDep:
    dependent: Annotated[DependentService, Inject(name="1")]


@service
class ServiceWithUnamedDep:
    dependent: Annotated[DependentService, Inject]


class Interface:
    pass


@service(provides=Interface, name="impl1")
class Impl1(Interface):
    pass


@service(provides=Interface, name="impl2")
class Impl2(Interface):
    pass


async def test_dependency_with_name(ioc: Container):
    ioc.register(DependentService)
    ioc.register(ServiceWithNamedDep)

    instance = await ioc.get(ServiceWithNamedDep)
    dependent = instance.dependent
    assert isinstance(dependent, DependentService)


async def test_dependency_without_name_should_fail(ioc: Container):
    ioc.register(DependentService)
    ioc.register(ServiceWithUnamedDep)

    with pytest.raises(ServiceNotFoundError):
        await ioc.get(ServiceWithUnamedDep)


async def test_default_dependency(ioc: Container):
    @service
    class Service:
        pass

    @service
    class WithNamedDep:
        dependent: Annotated[Service, Inject(name="1")]

    ioc.register(Service)
    ioc.register(WithNamedDep)

    with pytest.warns(UserWarning):
        instance = await ioc.get(WithNamedDep)

    dependent = instance.dependent
    assert isinstance(dependent, Service)


async def test_register_two_services_with_the_same_name_should_fail(ioc: Container):
    ioc.register(DependentService)
    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(DependentService)


async def test_dependencies_with_same_interface(ioc: Container):
    ioc.register(Impl1)
    ioc.register(Impl2)

    service1 = await ioc.get(Interface, name="impl1")
    service2 = await ioc.get(Interface, name="impl2")

    assert service1 is not service2
