from typing import Optional

from selva.di import Container, Scope

from .fixtures import ioc


class DependentService:
    pass


class ServiceWithOptionalDep:
    def __init__(self, dependent: Optional[DependentService]):
        self.dependent = dependent


class ServiceWithOptionalDepNone:
    def __init__(self, dependent: DependentService = None):
        self.dependent = dependent


class ServiceWithOptionalDepOrNone:
    def __init__(self, dependent: DependentService | None):
        self.dependent = dependent


class LazyDependency:
    def method(self):
        return 1


async def test_optional_dependency(ioc: Container):
    ioc.register(ServiceWithOptionalDep, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDep)
    assert service.dependent is None

    ioc.register(DependentService, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDep)
    assert isinstance(service.dependent, DependentService)


async def test_optional_dependency_with_none_as_default(ioc: Container):
    ioc.register(ServiceWithOptionalDepNone, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDepNone)
    assert service.dependent is None

    ioc.register(DependentService, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDepNone)
    assert isinstance(service.dependent, DependentService)


async def test_optional_dependency_with_or_none(ioc: Container):
    ioc.register(ServiceWithOptionalDepOrNone, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDepOrNone)
    assert service.dependent is None

    ioc.register(DependentService, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDepOrNone)
    assert isinstance(service.dependent, DependentService)

