from typing import Annotated
from types import SimpleNamespace

import pytest

from selva.di.container import Container
from selva.di.decorator import resource, service
from selva.di.error import ServiceWithResourceDependencyError
from selva.di.inject import Inject


@resource
class Resource:
    def method(self) -> int:
        return 1


@service
class ServiceWithResource:
    async def method_with_resource(self, dep: Resource = ...) -> int:
        return dep.method()


@service
class ServiceWithResourceDependency:
    resource: Annotated[Resource, Inject]


@service
def service_with_resource_dependency_factory(res: Resource) -> ServiceWithResourceDependency:
    return ServiceWithResourceDependency(resource=res)


async def test_resource_same_context(ioc: Container):
    ioc.register(Resource)

    class Context:
        pass

    context = Context()
    instance1 = await ioc.get(Resource, context=context)
    instance2 = await ioc.get(Resource, context=context)

    assert instance1 is instance2


async def test_resource_distinct_contexts(ioc: Container):
    ioc.register(Resource)

    class Context:
        pass

    context1 = Context()
    context2 = Context()

    instance1 = await ioc.get(Resource, context=context1)
    instance2 = await ioc.get(Resource, context=context2)

    assert instance1 is not instance2


async def test_service_with_resource(ioc: Container):
    ioc.register(Resource)
    ioc.register(ServiceWithResource)

    instance = await ioc.get(ServiceWithResource)

    result = await instance.method_with_resource()
    assert result == 1


async def test_service_with_resource_dependency_should_fail(ioc: Container):
    ioc.register(Resource)
    ioc.register(ServiceWithResourceDependency)

    with pytest.raises(ServiceWithResourceDependencyError):
        await ioc.get(ServiceWithResourceDependency)


async def test_factory_with_resource_dependency_should_fail(ioc: Container):
    ioc.register(Resource)
    ioc.register(service_with_resource_dependency_factory)

    with pytest.raises(ServiceWithResourceDependencyError):
        await ioc.get(ServiceWithResourceDependency)
