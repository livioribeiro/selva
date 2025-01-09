from typing import Annotated

import pytest

from selva.di.error import (
    FactoryMissingReturnTypeError,
    InvalidDependencyAnnotationError,
    ServiceWithUntypedDependencyError,
)
from selva.di.inject import Inject
from selva.di.service.model import ServiceDependency, ServiceSpec
from selva.di.service.parse import parse_service_spec


def test_parse_service_spec():
    def factory(dependency: Annotated[str, Inject]) -> object:
        pass

    result = parse_service_spec(factory)
    assert result == ServiceSpec(
        service=object,
        impl=None,
        factory=factory,
        name=None,
        dependencies=[("dependency", ServiceDependency(service=str, name=None))],
        initializer=None,
        finalizer=None,
    )


def test_factory_missing_return_type_should_fail():
    def factory():
        pass

    with pytest.raises(FactoryMissingReturnTypeError):
        parse_service_spec(factory)


def test_parse_service_spec_dependency_without_annotation():
    def factory(dependency: str) -> object:
        pass

    result = parse_service_spec(factory)
    assert result == ServiceSpec(
        service=object,
        impl=None,
        factory=factory,
        name=None,
        dependencies=[("dependency", ServiceDependency(service=str, name=None))],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_spec_with_name():
    def factory() -> object:
        pass

    result = parse_service_spec(factory, name="service")
    assert result == ServiceSpec(
        service=object,
        impl=None,
        factory=factory,
        name="service",
        dependencies=[],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_spec_more_dependencies():
    def factory(dependency: Annotated[str, Inject], other: int) -> object:
        pass

    result = parse_service_spec(factory)
    assert result == ServiceSpec(
        service=object,
        impl=None,
        factory=factory,
        name=None,
        dependencies=[
            ("dependency", ServiceDependency(service=str, name=None)),
            ("other", ServiceDependency(service=int, name=None)),
        ],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_spec_optional_dependency():
    def factory(dependency: Annotated[str, Inject] = None) -> object:
        pass

    result = parse_service_spec(factory)
    assert result == ServiceSpec(
        service=object,
        impl=None,
        factory=factory,
        name=None,
        dependencies=[
            ("dependency", ServiceDependency(service=str, name=None, optional=True))
        ],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_spec_named_dependency():
    def factory(dependency: Annotated[str, Inject(name="test")]) -> object:
        pass

    result = parse_service_spec(factory)
    assert result == ServiceSpec(
        service=object,
        impl=None,
        factory=factory,
        name=None,
        dependencies=[("dependency", ServiceDependency(service=str, name="test"))],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_with_annotated_non_dependency_should_fail():
    def factory(
        dependency: Annotated[str, Inject], property: Annotated[int, object]
    ) -> object:
        pass

    with pytest.raises(InvalidDependencyAnnotationError):
        parse_service_spec(factory)


def test_factory_with_untyped_dependency_should_fail():
    def factory(dependency) -> object:
        pass

    with pytest.raises(ServiceWithUntypedDependencyError):
        parse_service_spec(factory)
