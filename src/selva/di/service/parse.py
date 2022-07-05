import inspect
import typing
import warnings
from collections.abc import Callable
from types import NoneType, UnionType
from typing import Annotated, Any, Optional, TypeVar, Union

from selva.di.decorators import DI_FINALIZER_ATTRIBUTE, DI_INITIALIZER_ATTRIBUTE
from selva.di.errors import (
    FactoryMissingReturnTypeError,
    IncompatibleTypesError,
    InvalidServiceTypeError,
    MultipleNameAnnotationsError,
    NonInjectableTypeError,
    TypeVarInGenericServiceError,
)
from selva.di.service.model import InjectableType, ServiceDefinition, ServiceDependency


def _get_optional(type_hint) -> tuple[type, bool]:
    if typing.get_origin(type_hint) is UnionType:
        type_args = list(typing.get_args(type_hint))
        if NoneType in type_args:
            type_args.remove(NoneType)
            type_arg = type_args[0]
            return type_arg, True

    if typing.get_origin(type_hint) is Union:
        type_arg = typing.get_args(type_hint)[0]
        if type_hint == Optional[type_arg]:
            return type_arg, True

    return type_hint, False


def _get_annotations(type_hint) -> tuple[type, list[Any]]:
    if typing.get_origin(type_hint) is Annotated:
        type_hint, *annotations = typing.get_args(type_hint)
        return type_hint, annotations
    return type_hint, []


def get_dependencies(service: InjectableType) -> list[tuple[str, ServiceDependency]]:
    if inspect.isclass(service):
        types = typing.get_type_hints(service.__init__, include_extras=True)
    elif inspect.isfunction(service) or inspect.ismethod(service):
        types = typing.get_type_hints(service, include_extras=True)
    elif call := getattr(service, "__call__", None):
        types = typing.get_type_hints(call, include_extras=True)
    else:
        raise InvalidServiceTypeError(service)

    types.pop("return", None)

    result = []

    for name, type_hint in types.items():
        type_hint, optional = _get_optional(type_hint)
        type_hint, annotations = _get_annotations(type_hint)

        # in case Optional is wrapped in Annotated
        if not optional:
            type_hint, optional = _get_optional(type_hint)

        dependency_names = [a for a in annotations if isinstance(a, str)]
        if len(dependency_names) > 1:
            raise MultipleNameAnnotationsError(dependency_names, name, service)
        dependency_name = dependency_names[0] if len(dependency_names) == 1 else None

        service_dependency = ServiceDependency(
            type_hint, optional=optional, name=dependency_name
        )
        result.append((name, service_dependency))

    return result


def _parse_definition_class(
    service: type, provides: type | None
) -> tuple[type, list[Callable], list[Callable]]:
    initializers = []
    finalizers = []

    if provides:
        origin = typing.get_origin(provides)
        if origin:
            if any(isinstance(a, TypeVar) for a in typing.get_args(provides)):
                raise TypeVarInGenericServiceError(provides)

            orig_bases = getattr(service, "__orig_bases__", None)
            if orig_bases and provides not in orig_bases:
                raise IncompatibleTypesError(service, provides)

        if not issubclass(service, origin or provides):
            raise IncompatibleTypesError(service, provides)

    provided_service = provides or service

    # get initializers and finalizers for service class
    for _, function in inspect.getmembers(service, inspect.isfunction):
        if getattr(function, DI_INITIALIZER_ATTRIBUTE, None):
            initializers.append(function)
        if getattr(function, DI_FINALIZER_ATTRIBUTE, None):
            finalizers.append(function)

    return provided_service, initializers, finalizers


def _parse_definition_factory(
    service: Callable, provides: type | None
) -> tuple[type, Callable | None]:
    finalizer = None

    if provides:
        message = "option 'provides' on a factory function has no effect"
        warnings.warn(message)

    service_type = typing.get_type_hints(service).get("return")
    if service_type is None:
        raise FactoryMissingReturnTypeError(service)

    provided_service = service_type

    # get finalizer for service factory
    if func := getattr(service, DI_FINALIZER_ATTRIBUTE, None):
        finalizer = func

    return provided_service, finalizer


def parse_definition(
    service: InjectableType, provides: type = None
) -> ServiceDefinition:
    if inspect.isclass(service):
        provided_service, initializers, finalizers = _parse_definition_class(
            service, provides
        )
    elif inspect.isfunction(service):
        provided_service, finalizer = _parse_definition_factory(service, provides)
        initializers = []
        finalizers = [finalizer] if finalizer else []
    else:
        raise NonInjectableTypeError(service)

    dependencies = get_dependencies(service)

    return ServiceDefinition(
        provides=provided_service,
        factory=service,
        dependencies=dependencies,
        initializers=initializers,
        finalizers=finalizers,
    )
