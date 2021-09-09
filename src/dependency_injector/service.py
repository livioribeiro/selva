import inspect
import typing
from enum import IntEnum
from types import FunctionType
from typing import Annotated, Any, NamedTuple, Optional, Union

from .lazy import Lazy

InjectableType = Union[type, FunctionType]


class Scope(IntEnum):
    SINGLETON = 1
    DEPENDENT = 2
    TRANSIENT = 3


class ServiceInfo(NamedTuple):
    scope: Scope
    provides: Optional[type]


class ServiceDependency(NamedTuple):
    service: type
    lazy: bool = False
    optional: bool = False


class ServiceDefinition(NamedTuple):
    provides: type
    scope: Scope
    factory: InjectableType
    dependencies: list[tuple[str, ServiceDependency]]

    def accept_scope(self, scope: Scope) -> bool:
        return self.scope <= scope


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


def _get_lazy(type_hint) -> tuple[type, bool]:
    if typing.get_origin(type_hint) is Lazy:
        type_hint = typing.get_args(type_hint)[0]
        return type_hint, True
    return type_hint, False


def get_dependencies(service: InjectableType) -> list[tuple[str, ServiceDependency]]:
    if inspect.isclass(service):
        types = typing.get_type_hints(service.__init__, include_extras=True)
    else:
        types = typing.get_type_hints(service, include_extras=True)
        types.pop("return", None)

    result = []

    for name, type_hint in types.items():
        type_hint, optional = _get_optional(type_hint)
        type_hint, _annotations = _get_annotations(type_hint)  # for future use
        type_hint, lazy = _get_lazy(type_hint)

        service_dependency = ServiceDependency(type_hint, lazy=lazy, optional=optional)
        result.append((name, service_dependency))

    return result
