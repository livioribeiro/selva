import inspect
import typing
from collections.abc import Callable, Iterable
from types import NoneType, UnionType
from typing import Annotated, Any, Optional, TypeVar, Union

from loguru import logger

from selva.di.error import (
    FactoryMissingReturnTypeError,
    InvalidServiceTypeError,
    NonInjectableTypeError,
    TypeVarInGenericServiceError,
)
from selva.di.inject import Inject
from selva.di.service.model import InjectableType, ServiceDependency, ServiceSpec

DI_INITIALIZER = "initialize"
DI_FINALIZER = "finalize"


def _check_optional(type_hint: type, default: Any) -> tuple[type, bool]:
    is_optional = default is None

    if typing.get_origin(type_hint) is UnionType:
        type_args = list(typing.get_args(type_hint))
        if NoneType in type_args:
            type_args.remove(NoneType)

            type_hint = type_args[0]
            is_optional = True

    if typing.get_origin(type_hint) is Union:
        type_arg = typing.get_args(type_hint)[0]
        if type_hint == Optional[type_arg]:
            type_hint = type_arg
            is_optional = True

    return type_hint, is_optional


def _get_injectable_params(hint) -> tuple[type, Any] | None:
    if typing.get_origin(hint) is not Annotated:
        return None

    arg_type, arg_meta = typing.get_args(hint)[0:2]
    if not isinstance(arg_meta, Inject) and arg_meta is not Inject:
        return None

    return arg_type, arg_meta


def _get_service_signature(service: InjectableType) -> Iterable[tuple[str, type, Any]]:
    if inspect.isclass(service):
        for name, hint in typing.get_type_hints(service, include_extras=True).items():
            if params := _get_injectable_params(hint):
                arg_type, arg_meta = params
                yield name, arg_type, arg_meta
    elif inspect.isfunction(service):
        for name, param in inspect.signature(service).parameters.items():
            hint = param.annotation
            if params := _get_injectable_params(hint):
                arg_type, arg_meta = params
                yield name, arg_type, arg_meta
            else:
                yield name, hint, None
    else:
        raise InvalidServiceTypeError(service)


def get_dependencies(
    service: InjectableType,
) -> Iterable[tuple[str, ServiceDependency]]:
    for name, hint, meta in _get_service_signature(service):
        if isinstance(meta, Inject):
            service_name = meta.name
            meta = inspect.Parameter.empty
        else:
            service_name = None

        hint, is_optional = _check_optional(hint, meta)

        dependency = ServiceDependency(hint, name=service_name, optional=is_optional)
        yield name, dependency


def _parse_definition_class(
    service: type, provides: type | None
) -> tuple[type, Callable, Callable]:
    if provides and typing.get_origin(provides):
        if any(isinstance(a, TypeVar) for a in typing.get_args(provides)):
            raise TypeVarInGenericServiceError(provides)

    provided_service = provides or service

    initializer = getattr(service, DI_INITIALIZER, None)
    finalizer = getattr(service, DI_FINALIZER, None)

    return provided_service, initializer, finalizer


def _parse_definition_factory(service: Callable) -> type:
    service_type = typing.get_type_hints(service).get("return")
    if service_type is None:
        raise FactoryMissingReturnTypeError(service)

    provided_service = service_type

    return provided_service


def parse_service_spec(
    injectable: InjectableType,
    provides: type = None,
    name: str = None,
) -> ServiceSpec:
    if inspect.isclass(injectable):
        provided_service, initializer, finalizer = _parse_definition_class(
            injectable, provides
        )

        service = injectable
        factory = None
    elif inspect.isfunction(injectable):
        if provides:
            logger.warning("option 'provides' on a factory function has no effect")

        provided_service = _parse_definition_factory(injectable)
        initializer = None
        finalizer = None

        service = provided_service
        factory = injectable
    else:
        raise NonInjectableTypeError(injectable)

    dependencies = list(get_dependencies(injectable))

    return ServiceSpec(
        service=service,
        provides=provided_service,
        factory=factory,
        name=name,
        dependencies=dependencies,
        initializer=initializer,
        finalizer=finalizer,
    )
