import typing
import warnings
from typing import Optional, Union

from ..errors import ServiceAlreadyRegisteredError, ServiceNotFoundError
from .model import ServiceDefinition


class ServiceRecord:
    def __init__(self):
        self.providers: dict[Optional[str], ServiceDefinition] = {}

    def add(self, service: ServiceDefinition, name: str = None):
        if name in self.providers:
            raise ServiceAlreadyRegisteredError(service.provides, name)

        self.providers[name] = service

    def get(self, name: str = None) -> Optional[ServiceDefinition]:
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

    def __contains__(self, name: Optional[str]) -> bool:
        return name in self.providers


def _get_key_name(k: Union[type, tuple[type, str]]) -> tuple[type, Optional[str]]:
    if isinstance(k, type) or typing.get_origin(k) is not None:
        return k, None
    elif isinstance(k, tuple) and len(k) == 2:
        return k
    else:
        raise ValueError(k)


class ServiceRegistry:
    def __init__(self):
        self.data: dict[type, ServiceRecord] = {}

    def get(
        self, key: type, name: str = None, optional=False
    ) -> Optional[ServiceDefinition]:
        if optional and (key, name) not in self:
            return None
        return self[key, name]

    def __getitem__(self, k: Union[type, tuple[type, str]]):
        key, name = _get_key_name(k)

        if key in self.data and (service := self.data[key].get(name)) is not None:
            return service

        raise ServiceNotFoundError(key, name=name)

    def __setitem__(self, k: Union[type, tuple[type, str]], v: ServiceDefinition):
        key, name = _get_key_name(k)

        if key not in self.data:
            self.data[key] = ServiceRecord()

        self.data[key].add(v, name)

    def __contains__(self, k: Union[type, tuple[type, str]]):
        key, name = _get_key_name(k)
        return key in self.data and name in self.data[key]
