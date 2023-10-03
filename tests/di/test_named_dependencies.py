from typing import Annotated

import pytest

from selva.di.container import Container
from selva.di.error import ServiceAlreadyRegisteredError, ServiceNotFoundError
from selva.di.inject import Inject

from .fixtures import ioc


class DependentService:
    pass


class ServiceWithNamedDep:
    dependent: Annotated[DependentService, Inject("1")]


class ServiceWithUnamedDep:
    dependent: Annotated[DependentService, Inject]


class Interface:
    pass


class Impl1(Interface):
    pass


class Impl2(Interface):
    pass


async def test_dependency_with_name(ioc: Container):
    ioc.register(DependentService, name="1")
    ioc.register(ServiceWithNamedDep)

    service = await ioc.get(ServiceWithNamedDep)
    dependent = service.dependent
    assert isinstance(dependent, DependentService)


async def test_dependency_without_name_should_fail(ioc: Container):
    ioc.register(DependentService, name="1")
    ioc.register(ServiceWithUnamedDep)

    with pytest.raises(ServiceNotFoundError):
        await ioc.get(ServiceWithUnamedDep)


async def test_default_dependency(ioc: Container):
    ioc.register(DependentService)
    ioc.register(ServiceWithNamedDep)

    with pytest.warns(UserWarning):
        service = await ioc.get(ServiceWithNamedDep)

    dependent = service.dependent
    assert isinstance(dependent, DependentService)


async def test_register_two_services_with_the_same_name_should_fail(ioc: Container):
    ioc.register(DependentService, name="1")
    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(DependentService, name="1")


async def test_dependencies_with_same_interface(ioc: Container):
    ioc.register(Impl1, provides=Interface, name="impl1")
    ioc.register(Impl2, provides=Interface, name="impl2")

    service1 = await ioc.get(Interface, name="impl1")
    service2 = await ioc.get(Interface, name="impl2")

    assert service1 is not service2
