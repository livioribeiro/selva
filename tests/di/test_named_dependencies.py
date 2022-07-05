from typing import Annotated

import pytest

from selva.di import Container
from selva.di.service.named import Named
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


class ServiceWithNamedAttribute:
    def __init__(self, dependent: Named[DependentService, "1"]):
        self.dependent = dependent


class Interface:
    pass


class Impl1(Interface):
    pass


class Impl2(Interface):
    pass


async def test_dependency_with_name(ioc: Container):
    ioc.register(DependentService, name="1")
    ioc.register(ServiceWithNamedDep)

    service = await ioc.get(ServiceWithNamedDep)
    dependent = service.dependent
    assert isinstance(dependent, DependentService)


async def test_default_dependency(ioc: Container):
    ioc.register(DependentService)
    ioc.register(ServiceWithNamedDep)

    with pytest.warns(UserWarning):
        service = await ioc.get(ServiceWithNamedDep)

    dependent = service.dependent
    assert isinstance(dependent, DependentService)


async def test_multiple_name_annotations_should_fail(ioc: Container):
    with pytest.raises(MultipleNameAnnotationsError):
        ioc.register(ServiceWithMultiNameAnnotations)


async def test_register_two_services_with_the_same_name_should_fail(ioc: Container):
    ioc.register(DependentService, name="1")
    with pytest.raises(ServiceAlreadyRegisteredError):
        ioc.register(DependentService, name="1")


async def test_dependency_with_named_attribute(ioc: Container):
    ioc.register(DependentService, name="1")
    ioc.register(ServiceWithNamedAttribute)

    service = await ioc.get(ServiceWithNamedAttribute)
    dependent = service.dependent
    assert isinstance(dependent, DependentService)


async def test_dependencies_with_same_interface(ioc: Container):
    ioc.register(Impl1, provides=Interface, name="impl1")
    ioc.register(Impl2, provides=Interface, name="impl2")

    service1 = await ioc.get(Interface, name="impl1")
    service2 = await ioc.get(Interface, name="impl2")

    assert service1 is not service2


def test_named_with_one_args_should_fail():
    class TestClass:
        pass

    with pytest.raises(ValueError):
        Named[TestClass]


def test_named_with_too_much_arguments_should_fail():
    class TestClass:
        pass

    with pytest.raises(ValueError):
        Named[TestClass, "name", 1]


def test_named_with_wrong_argument_types_should_fail():
    class TestClass:
        pass

    with pytest.raises(ValueError):
        Named[TestClass, 1]

    with pytest.raises(ValueError):
        Named[1, "name"]


def test_new_named_should_fail():
    with pytest.raises(TypeError):
        Named()
