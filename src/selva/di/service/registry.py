import typing
import warnings
from collections import defaultdict

from ..errors import ServiceAlreadyRegisteredError, ServiceNotFoundError
from .model import ServiceDefinition


class ServiceRecord:
    def __init__(self):
        self.providers: dict[str | None, ServiceDefinition] = {}

    def add(self, service: ServiceDefinition, name: str = None):
        if name in self.providers:
            raise ServiceAlreadyRegisteredError(service.provides, name)

        self.providers[name] = service

    def get(self, name: str = None) -> ServiceDefinition | None:
        if service := self.providers.get(name):
            return service

        if default := self.providers.get(None):
            message = (
                f"using default service instead of '{name}'"
                f" for '{default.provides.__qualname__}'"
            )

            warnings.warn(message)
            return default

        return None

    def __contains__(self, name: str | None) -> bool:
        return name in self.providers


def _get_key_with_name(key: type | tuple[type, str]) -> tuple[type, str | None]:
    # typing.get_origin(k) to test Generic[T]
    if isinstance(key, type) or typing.get_origin(key) is not None:
        return key, None

    if isinstance(key, tuple) and len(key) == 2:
        return key

    raise ValueError(key)


class ServiceRegistry:
    def __init__(self):
        self.data: dict[type, ServiceRecord] = defaultdict(ServiceRecord)

    def get(self, key: type, name: str = None) -> ServiceDefinition | None:
        if (key, name) not in self:
            return None
        return self[key, name]

    def __getitem__(self, key: type | tuple[type, str]):
        inner_key, name = _get_key_with_name(key)

        if service := self.data[inner_key].get(name):
            return service

        raise ServiceNotFoundError(inner_key, name=name)

    def __setitem__(self, key: type | tuple[type, str], value: ServiceDefinition):
        inner_key, name = _get_key_with_name(key)
        self.data[inner_key].add(value, name)

    def __contains__(self, key: type | tuple[type, str]):
        inner_key, name = _get_key_with_name(key)
        return inner_key in self.data and name in self.data[inner_key]
