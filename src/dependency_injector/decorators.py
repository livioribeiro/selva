from types import FunctionType
from typing import Union

from .service import Scope, ServiceInfo

InjectableType = Union[type, FunctionType]


def singleton(service: InjectableType = None, *, provides: type = None):
    return register(service, scope=Scope.SINGLETON, provides=provides)


def dependent(service: InjectableType = None, *, provides: type = None):
    return register(service, scope=Scope.DEPENDENT, provides=provides)


def transient(service: InjectableType = None, *, provides: type = None):
    return register(service, scope=Scope.TRANSIENT, provides=provides)


def register(service: InjectableType = None, *, scope: Scope, provides: type = None):
    def register_func(service: InjectableType):
        setattr(service, "__dependency_injector__", ServiceInfo(scope, provides))
        return service

    return register_func(service) if service else register_func
