from enum import IntEnum
from types import FunctionType
from typing import NamedTuple, Union

InjectableType = Union[type, FunctionType]


class Scope(IntEnum):
    SINGLETON = 1
    DEPENDENT = 2
    TRANSIENT = 3


class ServiceDefinition(NamedTuple):
    provides: type
    scope: Scope
    factory: InjectableType

    def accept_scope(self, scope: Scope) -> bool:
        return self.scope <= scope
