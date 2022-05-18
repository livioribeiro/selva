from typing import Optional

from ward import test

from dependency_injector import Scope

from .fixtures import ioc


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


@test("optional dependency")
async def _(ioc=ioc):
    ioc.register(ServiceWithOptionalDep, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDep)
    assert service.dependent is None

    ioc.register(DependentService, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDep)
    assert isinstance(service.dependent, DependentService)


@test("optional dependency with None as default value")
async def _(ioc=ioc):
    ioc.register(ServiceWithOptionalDepNone, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDepNone)
    assert service.dependent is None

    ioc.register(DependentService, Scope.TRANSIENT)
    service = await ioc.get(ServiceWithOptionalDepNone)
    assert isinstance(service.dependent, DependentService)

