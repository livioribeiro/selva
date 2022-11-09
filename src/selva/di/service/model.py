from collections.abc import Callable
from types import FunctionType
from typing import NamedTuple

InjectableType = type | FunctionType


class ServiceInfo(NamedTuple):
    provides: type | None
    name: str | None


class ServiceDependency(NamedTuple):
    service: type
    name: str | None
    optional: bool = False


class ServiceSpec(NamedTuple):
    service: type
    provides: type
    factory: FunctionType
    name: str | None
    dependencies: list[tuple[str, ServiceDependency]]
    initializer: Callable = None
    finalizer: Callable = None
