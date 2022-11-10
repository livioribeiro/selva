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
    """Declare a class or function as a service

    For classes, a constructor will be generated to help create instances
    outside the dependency injection context
    """
    def inner(arg: InjectableType) -> T:
        setattr(arg, DI_SERVICE_ATTRIBUTE, ServiceInfo(provides, name))

        if inspect.isclass(arg):
            annotations = set(inspect.get_annotations(arg).keys())
            dependencies = [d for d, _ in inspect.getmembers(arg, _is_inject)]

            if missing := [d for d in dependencies if d not in annotations]:
                # TODO: create exception
                raise TypeError(
                    f"Missing type annotation for dependencies of service '{arg.__qualname__}': "
                    ', '.join(missing)
                )

            def init(self, *args, **kwargs):
                """Generated init method for service

                Positional and keywork arguments will be set to declared dependencies.
                Dependencies without an argument to set their value will be None.
                Remaining arguments will be ignored.
                """

                positional_params = [d for d in dependencies if d not in kwargs.keys()]

                # set positional argument values
                values = dict(zip(positional_params, args))

                # set keyword argument values
                values |= {k: v for k, v in kwargs.items() if k in dependencies}

                # the rest of the dependencies will be set to None
                param_keys = values.keys()
                values |= {d: None for d in dependencies if d not in param_keys}

                for k, v in values.items():
                    setattr(self, k, v)

            setattr(arg, "__init__", init)

        return arg

    return inner(injectable) if injectable else inner
