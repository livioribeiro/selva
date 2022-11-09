import inspect
from collections.abc import Callable
from typing import Any

from .service.model import InjectableType


def _type_name(service):
    if (
        inspect.isclass(service)
        or inspect.isfunction(service)
        or inspect.ismethod(service)
    ):
        return service.__qualname__

    return str(service)


class DependencyInjectionError(Exception):
    pass


class DependencyLoopError(DependencyInjectionError):
    def __init__(self, dependency_stack: list[type]):
        loop = " -> ".join([dep.__name__ for dep in dependency_stack])
        super().__init__(f"dependency loop detected: {loop}")


class ServiceNotFoundError(DependencyInjectionError):
    def __init__(
        self,
        service: type,
        name: str = None,
    ):
        message = f"unable to find service '{_type_name(service)}'"
        if name is not None:
            message += f" with name '{name}'"

        super().__init__(message)


class NonInjectableTypeError(DependencyInjectionError):
    def __init__(self, service: Any):
        super().__init__(f"'{service}' is not injectable")


class FactoryMissingReturnTypeError(DependencyInjectionError):
    def __init__(self, factory: Callable):
        super().__init__(f"factory '{_type_name(factory)}' is missing return type")


class ServiceAlreadyRegisteredError(DependencyInjectionError):
    def __init__(self, service: type, name: str = None):
        message = f"service '{_type_name(service)}' is already registered"
        if name:
            message += f" with name '{name}'"

        super().__init__(message)


class TypeVarInGenericServiceError(DependencyInjectionError):
    def __init__(self, provided: type):
        super().__init__(f"{_type_name(provided)} has generic types")


class InvalidServiceTypeError(DependencyInjectionError):
    def __init__(self, service: Any):
        super().__init__(f"object of type {type(service)} is not a valid service")


class ServiceWithoutDecoratorError(DependencyInjectionError):
    def __init__(self, service: InjectableType):
        super().__init__(
            f"service {service.__module__}.{service.__qualname__}"
            " must be decorated with @service"
        )
