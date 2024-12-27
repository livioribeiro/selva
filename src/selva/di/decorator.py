import inspect
import typing
from collections.abc import Callable
from typing import TypeVar, dataclass_transform

from selva.di.error import NonInjectableTypeError, FactoryMissingReturnTypeError
from selva.di.service.model import ServiceInfo

__all__ = ("service", "DI_ATTRIBUTE_SERVICE")

DI_ATTRIBUTE_SERVICE = "__selva_di_service__"

T = TypeVar("T")


@dataclass_transform(eq_default=False)
def service(
    injectable: T = None,
    /,
    *,
    name: str = None,
    startup: bool = False,
) -> T | Callable[[T], T]:
    """Declare a function as a service factory"""

    def inner(inner_injectable) -> T:
        if not inspect.isfunction(inner_injectable):
            raise NonInjectableTypeError(injectable)

        setattr(inner_injectable, DI_ATTRIBUTE_SERVICE, ServiceInfo(name, startup))

        return inner_injectable

    return inner(injectable) if injectable else inner
