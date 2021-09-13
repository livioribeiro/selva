from typing import Annotated

import pytest

from dependency_injector import Name, Scope
from dependency_injector.errors import (
    MultipleNameAnnotationsError,
    ServiceAlreadyRegisteredError,
)

from . import ioc


class DependentService:
    pass


class ServiceWithNamedDep:
    def __init__(self, dependent: Annotated[DependentService, Name("1")]):
        self.dependent = dependent


class ServiceWithMultiNameAnnotations:
    def __init__(self, dependent: Annotated[DependentService, Name("1"), Name("2")]):
        self.dependent = dependent


def test_dependency_with_name(ioc):
    ioc.register(DependentService, Scope.TRANSIENT, name="1")
    ioc.register(ServiceWithNamedDep, Scope.TRANSIENT)

    service = ioc.get(ServiceWithNamedDep)
    dependent = service.dependent
    assert isinstance(dependent, DependentService)


def test_default_dependency(ioc):
    ioc.register(DependentService, Scope.TRANSIENT)
    ioc.register(ServiceWithNamedDep, Scope.TRANSIENT)

    with pytest.warns(UserWarning):
        service = ioc.get(ServiceWithNamedDep)

    dependent = service.dependent
    assert isinstance(dependent, DependentService)


def test_multiple_name_annotations_should_fail(ioc):
    with pytest.raises(MultipleNameAnnotationsError):
        ioc.register(ServiceWithMultiNameAnnotations, Scope.TRANSIENT)


def test_already_registerd_with_name_should_fail(ioc):
    ioc.register(DependentService, Scope.TRANSIENT, name="1")
    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(DependentService, Scope.TRANSIENT, name="1")
