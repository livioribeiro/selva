from typing import Annotated

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.inject import Inject


@service
class DependentService:
    pass


@service
class ServiceWithOptionalDep:
    dependent: Annotated[DependentService, Inject] = None


async def test_optional_dependency(ioc: Container):
    ioc.register(ServiceWithOptionalDep)
    instance = await ioc.get(ServiceWithOptionalDep)
    assert instance.dependent is None


async def test_optional_dependency_with_provided_dependency(ioc: Container):
    ioc.register(ServiceWithOptionalDep)
    ioc.register(DependentService)
    instance = await ioc.get(ServiceWithOptionalDep)
    assert isinstance(instance.dependent, DependentService)
