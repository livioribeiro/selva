from enum import IntEnum
from types import FunctionType
from typing import NamedTuple, Optional, Union

InjectableType = Union[type, FunctionType]


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
    optional: bool = False


class ServiceDefinition(NamedTuple):
    provides: type
    scope: Scope
    factory: InjectableType
    dependencies: list[tuple[str, ServiceDependency]]

    def accept_scope(self, scope: Scope) -> bool:
        return self.scope <= scope
