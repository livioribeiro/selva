from typing import Annotated, Optional

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.inject import Inject


@service
class DependentService:
    pass


@service
class ServiceWithOptionalDep:
    dependent: Annotated[Optional[DependentService], Inject]


@service
class ServiceWithOptionalDepOrNone:
    dependent: Annotated[DependentService | None, Inject]


async def test_optional_dependency(ioc: Container):
    ioc.register(ServiceWithOptionalDep)
    instance = await ioc.get(ServiceWithOptionalDep)
    assert instance.dependent is None

    ioc.store.clear()

    ioc.register(DependentService)
    instance = await ioc.get(ServiceWithOptionalDep)
    assert isinstance(instance.dependent, DependentService)


async def test_optional_dependency_with_or_none(ioc: Container):
    ioc.register(ServiceWithOptionalDepOrNone)
    service = await ioc.get(ServiceWithOptionalDepOrNone)
    assert service.dependent is None

    ioc.store.clear()

    ioc.register(DependentService)
    service = await ioc.get(ServiceWithOptionalDepOrNone)
    assert isinstance(service.dependent, DependentService)
