import inspect
from types import FunctionType
from typing import Any

from selva.di.service.model import InjectableType


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
    def __init__(
        self, stack: list[tuple[type, str | None]], conflict: tuple[type, str | None]
    ):
        conflict_index = stack.index(conflict)
        last_index = len(stack) - 1

        loop_stack = []
        for i, (dep, name) in enumerate(stack):
            if i == conflict_index:
                indicator = "┌"
            elif i < last_index:
                indicator = "│"
            elif i == last_index:
                indicator = "└"
            else:
                indicator = " "

            dependency = f"{dep.__module__}.{dep.__name__}"
            name = f" ({name})" if name else ""
            loop_stack.append(f"{indicator} {dependency}{name}")

        result = "\n".join(loop_stack)
        super().__init__(f"dependency loop detected: \n{result}")


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
    def __init__(self, factory: FunctionType):
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


class ServiceWithUntypedDependencyError(DependencyInjectionError):
    def __init__(self, service: InjectableType, param: str):
        super().__init__(
            f"service {service.__module__}.{service.__qualname__}"
            f" must annotate parameter '{param}'"
        )


class InvalidDependencyAnnotationError(DependencyInjectionError):
    def __init__(self, dependency, annotation):
        super().__init__(
            f"dependency '{dependency}' has invalid annotation '{annotation}'"
        )
