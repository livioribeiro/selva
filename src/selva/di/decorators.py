import inspect
from collections.abc import Callable
from typing import TypeVar

from selva.di.inject import Inject
from selva.di.service.model import InjectableType, ServiceInfo

__all__ = ("service", "DI_SERVICE_ATTRIBUTE")

DI_SERVICE_ATTRIBUTE = "__selva_di_service__"

T = TypeVar("T", bound=InjectableType)


def _is_inject(value) -> bool:
    return isinstance(value, Inject) or value is Inject


def service(
    injectable: T = None, /, *, provides: type = None, name: str = None
) -> T | Callable[[T], T]:
    def inner(arg: InjectableType) -> T:
        setattr(arg, DI_SERVICE_ATTRIBUTE, ServiceInfo(provides, name))

        if inspect.isclass(arg):
            annotations = set(inspect.get_annotations(arg).keys())

            missing = []
            for prop, _ in inspect.getmembers(arg, _is_inject):
                if prop not in annotations:
                    missing.append(prop)

            if missing:
                # TODO: create exception
                raise TypeError(
                    f"Missing type annotation for dependencies of service '{arg.__qualname__}': "
                    ', '.join(missing)
                )

        return arg

    return inner(injectable) if injectable else inner
