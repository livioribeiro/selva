from collections.abc import Callable
from types import FunctionType, MethodType
from typing import NamedTuple

InjectableType = type | FunctionType | MethodType


class ServiceInfo(NamedTuple):
    provides: type | None
    name: str | None


class ServiceDependency(NamedTuple):
    service: type
    name: str | None
    optional: bool = False


class ServiceDefinition(NamedTuple):
    provides: type
    factory: InjectableType
    dependencies: list[tuple[str, ServiceDependency]]
    initializers: list[Callable]
    finalizers: list[Callable]
