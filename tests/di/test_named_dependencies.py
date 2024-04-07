from typing import Annotated

import pytest

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import ServiceAlreadyRegisteredError, ServiceNotFoundError
from selva.di.inject import Inject


@service(name="1")
class NamedService:
    pass


@service
class ServiceWithNamedDep:
    dependent: Annotated[NamedService, Inject(name="1")]


class Interface:
    pass


@service(provides=Interface, name="impl1")
class Impl1(Interface):
    pass


@service(provides=Interface, name="impl2")
class Impl2(Interface):
    pass


async def test_dependency_with_name(ioc: Container):
    ioc.register(NamedService)
    ioc.register(ServiceWithNamedDep)

    instance = await ioc.get(ServiceWithNamedDep)
    dependent = instance.dependent
    assert isinstance(dependent, NamedService)


async def test_unnamed_dependency_with_named_service_should_fail(ioc: Container):
    @service
    class Service:
        pass

    @service
    class DependentService:
        dependent: Annotated[Service, Inject(name="1")]

    ioc.register(NamedService)
    ioc.register(DependentService)

    with pytest.raises(ServiceNotFoundError):
        await ioc.get(DependentService)


async def test_named_dependency_with_unnamed_service_should_fail(ioc: Container):
    @service(name="1")
    class Service:
        pass

    @service
    class DependentService:
        dependent: Annotated[Service, Inject]

    ioc.register(NamedService)
    ioc.register(DependentService)

    with pytest.raises(ServiceNotFoundError):
        await ioc.get(DependentService)


async def test_register_two_services_with_the_same_name_should_fail(ioc: Container):
    ioc.register(NamedService)
    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(NamedService)


async def test_dependencies_with_same_interface(ioc: Container):
    ioc.register(Impl1)
    ioc.register(Impl2)

    service1 = await ioc.get(Interface, name="impl1")
    service2 = await ioc.get(Interface, name="impl2")

    assert service1 is not service2
