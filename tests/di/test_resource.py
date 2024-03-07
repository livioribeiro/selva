from typing import Annotated

import pytest

from selva.di.container import Container
from selva.di.decorator import resource, service
from selva.di.error import ServiceWithResourceDependencyError
from selva.di.inject import Inject


@resource
class Resource:
    pass


@service
class Service:
    resource: Annotated[Resource, Inject]


@service
def service_factory(res: Resource) -> Service:
    return Service(resource=res)


async def test_resource(ioc: Container):
    ioc.register(Resource)

    instance1 = await ioc.get(Resource)
    instance2 = await ioc.get(Resource)

    assert instance1 is not instance2


async def test_service_with_resource_dependency_should_fail(ioc: Container):
    ioc.register(Resource)
    ioc.register(Service)

    with pytest.raises(ServiceWithResourceDependencyError):
        await ioc.get(Service)


async def test_factory_with_resource_dependency_should_fail(ioc: Container):
    ioc.register(Resource)
    ioc.register(service_factory)

    with pytest.raises(ServiceWithResourceDependencyError):
        await ioc.get(Service)
