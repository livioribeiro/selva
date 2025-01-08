import inspect
import typing
from collections.abc import Callable, Iterable
from typing import Annotated, Any, TypeVar

import structlog

from selva.di.error import (
    FactoryMissingReturnTypeError,
    InvalidDependencyAnnotationError,
    InvalidServiceTypeError,
    ServiceWithUntypedDependencyError,
    TypeVarInGenericServiceError,
)
from selva.di.inject import Inject
from selva.di.service.model import InjectableType, ServiceDependency, ServiceSpec

DI_INITIALIZER = "initialize"
DI_FINALIZER = "finalize"

logger = structlog.get_logger()


def parse_service_spec(
    injectable: InjectableType,
    provides: type = None,
    name: str = None,
) -> ServiceSpec:
    if inspect.isclass(injectable):
        provided_service, initializer, finalizer = _parse_definition_class(
            injectable, provides
        )

        implementation = injectable
        factory = None
    elif inspect.isfunction(injectable):
        if provides:
            logger.warning(
                "option 'provides' on a factory function has no effect",
                factory=f"{injectable.__module__}.{injectable.__name__}",
            )

        provided_service = _parse_definition_factory(injectable)
        initializer = None
        finalizer = None

        implementation = None
        factory = injectable
    else:
        raise InvalidServiceTypeError(injectable)

    dependencies = list(get_dependencies(injectable))

    return ServiceSpec(
        service=provided_service,
        impl=implementation,
        factory=factory,
        name=name,
        dependencies=dependencies,
        initializer=initializer,
        finalizer=finalizer,
    )


def get_dependencies(
    service: InjectableType,
) -> Iterable[tuple[str, ServiceDependency]]:
    for name, hint, meta, is_optional in _get_service_signature(service):
        if isinstance(meta, Inject):
            service_name = meta.name
        else:
            service_name = None

        dependency = ServiceDependency(hint, name=service_name, optional=is_optional)
        yield name, dependency


def _get_service_signature(
    service: InjectableType,
) -> Iterable[tuple[str, type, Any, bool]]:
    if inspect.isclass(service):
        for name, hint in typing.get_type_hints(service, include_extras=True).items():
            try:
                params = _get_injectable_params(hint)
            except InvalidDependencyAnnotationError:
                continue

            if not params:
                continue

            arg_type, arg_meta = params
            is_optional = hasattr(service, name)
            yield name, arg_type, arg_meta, is_optional

    elif inspect.isfunction(service):
        for name, param in inspect.signature(service).parameters.items():
            hint = param.annotation
            if hint is inspect.Signature.empty:
                raise ServiceWithUntypedDependencyError(service, name)

            is_optional = param.default is not inspect.Parameter.empty
            if params := _get_injectable_params(hint):
                arg_type, arg_meta = params
                yield name, arg_type, arg_meta, is_optional
            else:
                yield name, hint, None, is_optional

    else:
        raise InvalidServiceTypeError(service)


def _get_injectable_params(hint) -> tuple[type, Any] | None:
    if typing.get_origin(hint) is not Annotated:
        return None

    arg_type, arg_meta = typing.get_args(hint)[0:2]
    if not isinstance(arg_meta, Inject) and arg_meta is not Inject:
        raise InvalidDependencyAnnotationError(arg_type, arg_meta)

    return arg_type, arg_meta


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
