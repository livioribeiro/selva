from typing import Optional

import pytest

from dependency_injector import Lazy, Scope

from . import ioc

pytestmark = pytest.mark.asyncio


class DependentService:
    pass


class ServiceWithOptionalDep:
    def __init__(self, dependent: Optional[DependentService]):
        self.dependent = dependent


class ServiceWithOptionalDepNone:
    def __init__(self, dependent: DependentService = None):
        self.dependent = dependent


class LazyDependency:
    def method(self):
        return 1


class ServiceWithLazyDep:
    def __init__(self, dependent: Lazy[LazyDependency]):
        self.dependent = dependent


async def test_optional_dependency(ioc):
    ioc.register(ServiceWithOptionalDep, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDep)
    assert service.dependent is None

    ioc.register(DependentService, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDep)
    assert isinstance(service.dependent, DependentService)


async def test_optional_dependency_default_none(ioc):
    ioc.register(ServiceWithOptionalDepNone, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDepNone)
    assert service.dependent is None

    ioc.register(DependentService, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDepNone)
    assert isinstance(service.dependent, DependentService)


async def test_lazy_dependency(ioc):
    ioc.register(LazyDependency, Scope.TRANSIENT)
    ioc.register(ServiceWithLazyDep, Scope.TRANSIENT)

    service = await ioc.get(ServiceWithLazyDep)
    dependent = await service.dependent.get()
    assert isinstance(dependent, LazyDependency)
    assert 1 == dependent.method()
