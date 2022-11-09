from typing import Optional

from selva.di.container import Container
from selva.di.inject import Inject

from .fixtures import ioc


class DependentService:
    pass


class ServiceWithOptionalDep:
    dependent: Optional[DependentService] = Inject()


class ServiceWithOptionalDepOrNone:
    dependent: DependentService | None = Inject()


async def test_optional_dependency(ioc: Container):
    ioc.register(ServiceWithOptionalDep)
    service = await ioc.get(ServiceWithOptionalDep)
    assert service.dependent is None

    ioc.store.clear()

    ioc.register(DependentService)
    service = await ioc.get(ServiceWithOptionalDep)
    assert isinstance(service.dependent, DependentService)


async def test_optional_dependency_with_or_none(ioc: Container):
    ioc.register(ServiceWithOptionalDepOrNone)
    service = await ioc.get(ServiceWithOptionalDepOrNone)
    assert service.dependent is None

    ioc.store.clear()

    ioc.register(DependentService)
    service = await ioc.get(ServiceWithOptionalDepOrNone)
    assert isinstance(service.dependent, DependentService)
