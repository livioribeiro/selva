from collections.abc import Callable
from enum import IntEnum
from types import FunctionType, MethodType
from typing import NamedTuple

InjectableType = type | FunctionType | MethodType


class Scope(IntEnum):
    SINGLETON = 1
    DEPENDENT = 2
    TRANSIENT = 3


class ServiceInfo(NamedTuple):
    scope: Scope
    provides: type | None
    name: str | None


class ServiceDependency(NamedTuple):
    service: type
    name: str | None
    optional: bool = False


class ServiceDefinition(NamedTuple):
    provides: type
    scope: Scope
    factory: InjectableType
    dependencies: list[tuple[str, ServiceDependency]]
    initializer: Callable | None
    finalizer: Callable | None

    def accept_scope(self, scope: Scope) -> bool:
        return self.scope <= scope
