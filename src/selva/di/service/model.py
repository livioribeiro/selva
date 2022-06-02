from collections.abc import Callable
from enum import IntEnum
from types import FunctionType, MethodType
from typing import NamedTuple, Optional

InjectableType = type | FunctionType | MethodType


class Scope(IntEnum):
    SINGLETON = 1
    DEPENDENT = 2
    TRANSIENT = 3


class ServiceInfo(NamedTuple):
    scope: Scope
    provides: Optional[type]
    name: Optional[str]


class ServiceDependency(NamedTuple):
    service: type
    name: Optional[str]
    optional: Optional[bool] = False


class ServiceDefinition(NamedTuple):
    provides: type
    scope: Scope
    factory: InjectableType
    dependencies: list[tuple[str, ServiceDependency]]
    initializer: Optional[Callable]
    finalizer: Optional[Callable]

    def accept_scope(self, scope: Scope) -> bool:
        return self.scope <= scope
