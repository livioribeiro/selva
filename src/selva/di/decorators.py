from types import FunctionType, MethodType
from typing import Union

from .service.model import Scope, ServiceInfo

DEPENDENCY_ATTRIBUTE = "__dependency__"

InjectableType = Union[type, FunctionType, MethodType]


def singleton(
    service: InjectableType = None, *, provides: type = None, name: str = None
):
    return register(service, scope=Scope.SINGLETON, provides=provides, name=name)


def dependent(
    service: InjectableType = None, *, provides: type = None, name: str = None
):
    return register(service, scope=Scope.DEPENDENT, provides=provides, name=name)


def transient(
    service: InjectableType = None, *, provides: type = None, name: str = None
):
    return register(service, scope=Scope.TRANSIENT, provides=provides, name=name)


def register(
    service: InjectableType = None,
    *,
    scope: Scope,
    provides: type = None,
    name: str = None
):
    def register_func(service: InjectableType):
        setattr(service, DEPENDENCY_ATTRIBUTE, ServiceInfo(scope, provides, name))
        return service

    return register_func(service) if service else register_func
