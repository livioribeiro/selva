from types import FunctionType
from typing import NamedTuple

InjectableType = type | FunctionType


class ServiceInfo(NamedTuple):
    name: str | None
    startup: bool = False


class ServiceSpec(NamedTuple):
    provides: type
    factory: FunctionType
    name: str | None
    receives_locator: bool
