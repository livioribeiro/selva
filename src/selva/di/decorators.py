import inspect
import functools
from collections.abc import Callable
from types import FunctionType, MethodType

from .service.model import Scope, ServiceInfo

DI_SERVICE_ATTRIBUTE = "__selva_di_service__"
DI_INITIALIZER_ATTRIBUTE = "__selva_di_initializer__"
DI_FINALIZER_ATTRIBUTE = "__selva_di_finalizer__"

InjectableType = type | FunctionType | MethodType


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
    def register_func(arg: InjectableType):
        setattr(arg, DI_SERVICE_ATTRIBUTE, ServiceInfo(scope, provides, name))
        return arg

    return register_func(service) if service else register_func


def initializer(func: Callable):
    setattr(func, DI_INITIALIZER_ATTRIBUTE, True)
    return func


def finalizer(func: Callable):
    if "self" in inspect.signature(func).parameters:
        setattr(func, DI_FINALIZER_ATTRIBUTE, True)
        return func

    @functools.wraps(func)
    def inner(target: Callable):
        setattr(target, DI_FINALIZER_ATTRIBUTE, func)
        return target

    return inner
