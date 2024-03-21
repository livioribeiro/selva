import inspect
import typing
from collections.abc import Callable
from typing import Annotated, TypeVar, dataclass_transform

from selva.di.inject import Inject
from selva.di.service.model import InjectableType, ServiceInfo

__all__ = ("service", "DI_ATTRIBUTE_SERVICE")

DI_ATTRIBUTE_SERVICE = "__selva_di_service__"

T = TypeVar("T")


def _is_inject(value) -> bool:
    origin = typing.get_origin(value)
    if not origin or origin is not Annotated:
        return False

    # if origin is Annotated, args has always at least 2 values
    args = typing.get_args(value)

    return isinstance(args[1], Inject) or args[1] is Inject


def _service(
    injectable: InjectableType,
    attribute_name: str,
    attribute_value,
) -> InjectableType:
    setattr(injectable, attribute_name, attribute_value)

    if inspect.isclass(injectable):
        dependencies = [
            dependency
            for dependency, annotation in inspect.get_annotations(injectable).items()
            if _is_inject(annotation)
        ]

        # save a reference to the original constructor
        original_init = getattr(injectable, "__init__", None)

        def init(self, *args, **kwargs):
            """Generated init method for service

            Positional and keyword arguments will be set to declared dependencies.
            Dependencies without an argument to set their value will be None.
            Remaining arguments will be ignored.
            """

            # call original constructor
            if original_init:
                original_init(self)

            positional_params = [d for d in dependencies if d not in kwargs]

            # set positional argument values
            values = dict(zip(positional_params, args))

            # set keyword argument values
            values |= {k: v for k, v in kwargs.items() if k in dependencies}

            # the rest of the dependencies will be set to None
            param_keys = values.keys()
            values |= {d: None for d in dependencies if d not in param_keys}

            for k, v in values.items():
                setattr(self, k, v)

        setattr(injectable, "__init__", init)

    return injectable


@dataclass_transform(eq_default=False)
def service(
    injectable: T = None,
    /,
    *,
    provides: type = None,
    name: str = None,
    startup: bool = False,
) -> T | Callable[[T], T]:
    """Declare a class or function as a service

    For classes, a constructor will be generated to help create instances
    outside the dependency injection context
    """

    def inner(inner_injectable) -> T:
        return _service(
            inner_injectable, DI_ATTRIBUTE_SERVICE, ServiceInfo(provides, name, startup)
        )

    return inner(injectable) if injectable else inner
