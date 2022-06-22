from typing import Annotated

import pytest

from selva.di import Container, Scope
from selva.di.errors import (
    MultipleNameAnnotationsError,
    ServiceAlreadyRegisteredError,
)

from .fixtures import ioc


class DependentService:
    pass


class ServiceWithNamedDep:
    def __init__(self, dependent: Annotated[DependentService, "1"]):
        self.dependent = dependent


class ServiceWithMultiNameAnnotations:
    def __init__(self, dependent: Annotated[DependentService, "1", "2"]):
        self.dependent = dependent


async def test_dependency_with_name(ioc: Container):
    ioc.register(DependentService, Scope.TRANSIENT, name="1")
    ioc.register(ServiceWithNamedDep, Scope.TRANSIENT)

    service = await ioc.get(ServiceWithNamedDep)
    dependent = service.dependent
    assert isinstance(dependent, DependentService)


async def test_default_dependency(ioc: Container):
    ioc.register(DependentService, Scope.TRANSIENT)
    ioc.register(ServiceWithNamedDep, Scope.TRANSIENT)

    with pytest.warns(UserWarning):
        service = await ioc.get(ServiceWithNamedDep)

    dependent = service.dependent
    assert isinstance(dependent, DependentService)


async def test_multiple_name_annotations_should_fail(ioc: Container):
    with pytest.raises(MultipleNameAnnotationsError):
        ioc.register(ServiceWithMultiNameAnnotations, Scope.TRANSIENT)


async def test_register_two_services_with_the_same_name_should_fail(ioc: Container):
    ioc.register(DependentService, Scope.TRANSIENT, name="1")
    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(DependentService, Scope.TRANSIENT, name="1")
