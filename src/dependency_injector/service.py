import inspect
import typing
from enum import IntEnum
from types import FunctionType
from typing import Annotated, NamedTuple, Optional, Union

from .errors import MultipleDependencyAnnotationError
from .annotations import Dependency

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
    optional: bool = False


class ServiceDefinition(NamedTuple):
    provides: type
    scope: Scope
    factory: InjectableType
    dependencies: list[tuple[str, ServiceDependency]]

    def accept_scope(self, scope: Scope) -> bool:
        return self.scope <= scope


def get_dependencies(service: InjectableType) -> list[tuple[str, ServiceDependency]]:
    if inspect.isclass(service):
        types = typing.get_type_hints(service.__init__)
    else:
        types = typing.get_type_hints(service)
        types.pop("return", None)

    result = []

    for name, type_hint in types.items():
        if typing.get_origin(type_hint) is Annotated:
            type_hint, *rest = typing.get_args(type_hint)
            dependency = [d for d in rest if isinstance(d, Dependency)]
            if len(dependency) > 1:
                raise MultipleDependencyAnnotationError(service, name)
            dependency = next(dependency, None)
            if dependency is not None:
                service_dependency = ServiceDependency(type_hint, optional=dependency.optional)
            else:
                service_dependency = ServiceDependency(type_hint)
        else:
            service_dependency = ServiceDependency(type_hint)

        result.append((name, service_dependency))

    return result
