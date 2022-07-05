import functools
import inspect
from collections.abc import Callable

from .service.model import InjectableType, ServiceInfo

DI_SERVICE_ATTRIBUTE = "__selva_di_service__"
DI_INITIALIZER_ATTRIBUTE = "__selva_di_initializer__"
DI_FINALIZER_ATTRIBUTE = "__selva_di_finalizer__"


def service(
    injectable: InjectableType = None, *, provides: type = None, name: str = None
):
    def inner(arg: InjectableType):
        setattr(arg, DI_SERVICE_ATTRIBUTE, ServiceInfo(provides, name))
        return arg

    return inner(injectable) if injectable else inner


def initializer(func: Callable):
    if not inspect.isfunction(func):
        raise TypeError(f"@initializer should be applied to a function or method")

    setattr(func, DI_INITIALIZER_ATTRIBUTE, True)
    return func


def finalizer(func: Callable):
    if not inspect.isfunction(func):
        raise TypeError(f"@finalizer should be applied to a function or method")

    if "self" in inspect.signature(func).parameters:
        setattr(func, DI_FINALIZER_ATTRIBUTE, True)
        return func

    @functools.wraps(func)
    def inner(target: Callable):
        setattr(target, DI_FINALIZER_ATTRIBUTE, func)
        return target

    return inner
