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
    impl: type | None
    factory: Callable | None
    name: str | None
    dependencies: list[tuple[str, ServiceDependency]]
    initializer: Callable | None = None
    finalizer: Callable | None = None
