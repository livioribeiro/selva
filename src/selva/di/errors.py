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


class InvalidScopeError(DependencyInjectionError):
    def __init__(
        self, service: type, scope: str, requested_scope: str, requester: type = None
    ):
        msg = f"service '{_type_name(service)}' with scope '{scope}'"

        if requester:
            msg += f", requested from '{_type_name(service)}'"

        msg += f" cannot be requested from scope '{requested_scope}'."

        super().__init__(msg)


class DependencyLoopError(DependencyInjectionError):
    def __init__(self, dependency_stack: list[type]):
        loop = " -> ".join([dep.__name__ for dep in dependency_stack])
        super().__init__(f"dependency loop detected: {loop}")


class IncompatibleTypesError(DependencyInjectionError):
    def __init__(self, implementation: type, interface: type):
        super().__init__(
            f"service '{_type_name(implementation)}'"
            f" does not derive from '{_type_name(interface)}'"
        )


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


class MissingDependentContextError(DependencyInjectionError):
    def __init__(self):
        super().__init__("context is required for DEPENDENT scope")


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


class CalledNonCallableError(DependencyInjectionError):
    def __init__(self, called: Any):
        super().__init__(f"{_type_name(called)} is not callable")


class TypeVarInGenericServiceError(DependencyInjectionError):
    def __init__(self, provided: type):
        super().__init__(f"{_type_name(provided)} has generic types")


class MultipleNameAnnotationsError(DependencyInjectionError):
    def __init__(self, names: list[str], parameter: str, service: InjectableType):
        super().__init__(
            f"multiple 'Name' annotations"
            f" for parameter '{parameter}"
            f" on service '{_type_name(service)}':"
            f" {', '.join(names)}"
        )


class InvalidServiceTypeError(DependencyInjectionError):
    def __init__(self, service: Any):
        super().__init__(f"object of type {type(service)} is not a valid service")


class ServiceWithoutDecoratorError(DependencyInjectionError):
    def __init__(self, service: InjectableType):
        super().__init__(
            f"service {service.__module__}.{service.__qualname__}"
            " must be decorated with @service"
        )


class InstanceNotDefinedError(DependencyInjectionError):
    def __init__(self, service: type):
        super().__init__(
            f"{service.__module__}.{service.__qualname__} must be defined"
            " for the given context"
        )
