import inspect
from types import FunctionType
from typing import Any, List


def _type_name(service):
    if inspect.isclass(service) or inspect.isfunction(service):
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
    def __init__(self, dependency_stack: List[type]):
        loop = " -> ".join([dep.__name__ for dep in dependency_stack])
        super().__init__(f"dependency loop detected: {loop}")


class IncompatibleTypesError(DependencyInjectionError):
    def __init__(self, implementation: type, interface: type):
        super().__init__(
            f"service '{_type_name(implementation)}'"
            f" does not derive from '{_type_name(interface)}'"
        )


class UnknownServiceError(DependencyInjectionError):
    def __init__(self, service: type):
        super().__init__(f"Service '{_type_name(service)}' is not known")


class MissingDependentContextError(DependencyInjectionError):
    def __init__(self):
        super().__init__("context is required for DEPENDENT scope")


class NonInjectableTypeError(DependencyInjectionError):
    def __init__(self, service: Any):
        super().__init__(f"'{service}' is not injectable")


class FactoryMissingReturnTypeError(DependencyInjectionError):
    def __init__(self, factory: FunctionType):
        super().__init__(f"factory '{_type_name(factory)}' is missing return type")


class ServiceAlreadyRegisteredError(DependencyInjectionError):
    def __init__(self, service: type):
        super().__init__(f"service '{_type_name(service)}' is already registered")


class CalledNonCallableError(DependencyInjectionError):
    def __init__(self, called: Any):
        super().__init__(f"{_type_name(called)} is not callable")


class TypeVarInGenericServiceError(DependencyInjectionError):
    def __init__(self, provided: type):
        super().__init__(f"{_type_name(provided)} has generic types")
