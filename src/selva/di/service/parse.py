import inspect
import typing
import warnings
from types import FunctionType
from typing import Annotated, Any, Optional, TypeVar, Union

from selva.di.errors import (
    FactoryMissingReturnTypeError,
    IncompatibleTypesError,
    MultipleNameAnnotationsError,
    NonInjectableTypeError,
    TypeVarInGenericServiceError,
)

from ..annotations import Name
from .model import InjectableType, Scope, ServiceDefinition, ServiceDependency


def _get_optional(type_hint) -> tuple[type, bool]:
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
    else:
        types = typing.get_type_hints(service, include_extras=True)

    types.pop("return", None)

    result = []

    for name, type_hint in types.items():
        type_hint, optional = _get_optional(type_hint)
        type_hint, annotations = _get_annotations(type_hint)

        # in case Optional is wrapped in Annotated
        if not optional:
            type_hint, optional = _get_optional(type_hint)

        dependency_names = [a.value for a in annotations if isinstance(a, Name)]
        if len(dependency_names) > 1:
            raise MultipleNameAnnotationsError(dependency_names, name, service)
        dependency_name = dependency_names[0] if len(dependency_names) == 1 else None

        service_dependency = ServiceDependency(
            type_hint, optional=optional, name=dependency_name
        )
        result.append((name, service_dependency))

    return result


def parse_definition(
    service: InjectableType, scope: Scope, provides: type = None
) -> ServiceDefinition:
    if inspect.isclass(service):
        service = typing.cast(type, service)
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
    elif inspect.isfunction(service):
        service = typing.cast(FunctionType, service)
        if provides:
            message = "option 'provides' on a factory function has no effect"
            warnings.warn(message)

        service_type = typing.get_type_hints(service).get("return")
        if service_type is None:
            raise FactoryMissingReturnTypeError(service)
        provided_service = service_type
    else:
        raise NonInjectableTypeError(service)

    dependencies = get_dependencies(service)

    return ServiceDefinition(
        provides=provided_service,
        scope=scope,
        factory=service,
        dependencies=dependencies,
    )
