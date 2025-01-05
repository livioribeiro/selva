from typing import Annotated

import pytest

from selva.di.inject import Inject
from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import ServiceWithUntypedDependencyError
from selva.di.service.model import ServiceSpec, ServiceDependency
from selva.di.service.parse import parse_service_spec, get_dependencies


def test_parse_service_spec():
    class ServiceClass:
        dependency: Annotated[str, Inject]

    result = parse_service_spec(ServiceClass)
    assert result == ServiceSpec(
        service=ServiceClass,
        impl=ServiceClass,
        factory=None,
        name=None,
        dependencies=[("dependency", ServiceDependency(service=str, name=None))],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_spec_with_interface():
    class ServiceClass:
        pass

    result = parse_service_spec(ServiceClass, provides=object)
    assert result == ServiceSpec(
        service=object,
        impl=ServiceClass,
        factory=None,
        name=None,
        dependencies=[],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_spec_with_name():
    class ServiceClass:
        pass

    result = parse_service_spec(ServiceClass, name="service")
    assert result == ServiceSpec(
        service=ServiceClass,
        impl=ServiceClass,
        factory=None,
        name="service",
        dependencies=[],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_spec_more_dependencies():
    class ServiceClass:
        dependency: Annotated[str, Inject]
        other: Annotated[int, Inject]

    result = parse_service_spec(ServiceClass)
    assert result == ServiceSpec(
        service=ServiceClass,
        impl=ServiceClass,
        factory=None,
        name=None,
        dependencies=[
            ("dependency", ServiceDependency(service=str, name=None)),
            ("other", ServiceDependency(service=int, name=None)),
        ],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_spec_optional_dependency():
    class ServiceClass:
        dependency: Annotated[str, Inject] = None

    result = parse_service_spec(ServiceClass)
    assert result == ServiceSpec(
        service=ServiceClass,
        impl=ServiceClass,
        factory=None,
        name=None,
        dependencies=[("dependency", ServiceDependency(service=str, name=None, optional=True))],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_spec_non_inject_dependency():
    class ServiceClass:
        dependency: Annotated[str, Inject]
        property: str

    result = parse_service_spec(ServiceClass)
    assert result == ServiceSpec(
        service=ServiceClass,
        impl=ServiceClass,
        factory=None,
        name=None,
        dependencies=[("dependency", ServiceDependency(service=str, name=None))],
        initializer=None,
        finalizer=None,
    )

def test_parse_service_spec_named_dependency():
    class ServiceClass:
        dependency: Annotated[str, Inject(name="test")]

    result = parse_service_spec(ServiceClass)
    assert result == ServiceSpec(
        service=ServiceClass,
        impl=ServiceClass,
        factory=None,
        name=None,
        dependencies=[("dependency", ServiceDependency(service=str, name="test"))],
        initializer=None,
        finalizer=None,
    )


def test_parse_service_with_annotated_non_dependency():
    class ServiceClass:
        dependency: Annotated[str, Inject]
        property: Annotated[int, object]

    result = parse_service_spec(ServiceClass)
    assert result == ServiceSpec(
        service=ServiceClass,
        impl=ServiceClass,
        factory=None,
        name=None,
        dependencies=[("dependency", ServiceDependency(service=str, name=None))],
        initializer=None,
        finalizer=None,
    )
