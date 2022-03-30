from typing import Annotated
import warnings

from ward import test, raises

from dependency_injector import Name, Scope
from dependency_injector.errors import (
    MultipleNameAnnotationsError,
    ServiceAlreadyRegisteredError,
)

from .fixtures import ioc


class DependentService:
    pass


class ServiceWithNamedDep:
    def __init__(self, dependent: Annotated[DependentService, Name("1")]):
        self.dependent = dependent


class ServiceWithMultiNameAnnotations:
    def __init__(self, dependent: Annotated[DependentService, Name("1"), Name("2")]):
        self.dependent = dependent


@test("dependency with name")
async def _(ioc=ioc):
    ioc.register(DependentService, Scope.TRANSIENT, name="1")
    ioc.register(ServiceWithNamedDep, Scope.TRANSIENT)

    service = await ioc.get(ServiceWithNamedDep)
    dependent = service.dependent
    assert isinstance(dependent, DependentService)


@test("default dependency")
async def _(ioc=ioc):
    ioc.register(DependentService, Scope.TRANSIENT)
    ioc.register(ServiceWithNamedDep, Scope.TRANSIENT)

    with warnings.catch_warnings(record=True) as w:
        service = await ioc.get(ServiceWithNamedDep)
        assert (
            f"using default service instead of '1' for '{DependentService.__name__}'"
            == str(w[0].message)
        )

    dependent = service.dependent
    assert isinstance(dependent, DependentService)


@test("multiple name annotations should fail")
async def _(ioc=ioc):
    with raises(MultipleNameAnnotationsError):
        ioc.register(ServiceWithMultiNameAnnotations, Scope.TRANSIENT)


@test("register two services with the same name should fail")
async def test_(ioc=ioc):
    ioc.register(DependentService, Scope.TRANSIENT, name="1")
    with raises(ServiceAlreadyRegisteredError):
        ioc.register(DependentService, Scope.TRANSIENT, name="1")
