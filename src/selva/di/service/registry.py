import typing
import warnings
from collections import defaultdict

from selva.di.errors import ServiceAlreadyRegisteredError, ServiceNotFoundError
from selva.di.service.model import ServiceSpec

__all__ = ("ServiceRecord", "ServiceRegistry")


class ServiceRecord:
    def __init__(self):
        self.providers: dict[str | None, ServiceSpec] = {}

    def add(self, service: ServiceSpec, name: str = None):
        if name in self.providers:
            raise ServiceAlreadyRegisteredError(service.provides, name)

        self.providers[name] = service

    def get(self, name: str = None) -> ServiceSpec | None:
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
        self.services: dict[type, ServiceRecord] = defaultdict(ServiceRecord)

    def get(self, key: type, name: str = None) -> ServiceSpec | None:
        if (key, name) not in self:
            return None
        return self[key, name]

    def __getitem__(self, key: type | tuple[type, str]):
        inner_key, name = _get_key_with_name(key)

        if service := self.services[inner_key].get(name):
            return service

        raise ServiceNotFoundError(inner_key, name=name)

    def __setitem__(self, key: type | tuple[type, str], value: ServiceSpec):
        inner_key, name = _get_key_with_name(key)
        self.services[inner_key].add(value, name)

    def __contains__(self, key: type | tuple[type, str]):
        inner_key, name = _get_key_with_name(key)
        return inner_key in self.services and name in self.services[inner_key]
