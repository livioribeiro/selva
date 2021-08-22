from types import FunctionType
from typing import Any, List


class DependencyInjectionError(Exception):
    pass


class InvalidScopeError(DependencyInjectionError):
    def __init__(
        self, service: type, scope: str, requested_scope: str, requester: type = None
    ):
        msg = f"service '{service.__qualname__}' with scope '{scope}'"

        if requester:
            msg += f", requested from '{service.__qualname__}'"

        msg += f" cannot be requested from scope '{requested_scope}'."

        super().__init__(msg)


class DependencyLoopError(DependencyInjectionError):
    def __init__(self, dependency_stack: List[type]):
        loop = " -> ".join([dep.__name__ for dep in dependency_stack])
        super().__init__(f"dependency loop detected: {loop}")


class IncompatibleTypesError(DependencyInjectionError):
    def __init__(self, service: type, interface: type):
        super().__init__(
            f"service '{service.__qualname__}'"
            f" does not derive from '{interface.__qualname__}'"
        )


class UnknownServiceError(DependencyInjectionError):
    def __init__(self, service: type):
        super().__init__(f"Service '{service.__qualname__}' is not known")


class MissingDependentContextError(DependencyInjectionError):
    def __init__(self):
        super().__init__("context is required for DEPENDENT scope")


class NonInjectableTypeError(DependencyInjectionError):
    def __init__(self, service: Any):
        super().__init__(f"'{service}' is not injectable")


class FactoryMissingReturnTypeError(DependencyInjectionError):
    def __init__(self, factory: FunctionType):
        super().__init__(f"factory '{factory.__qualname__}' is missing return type")


class ServiceAlreadyRegisteredError(DependencyInjectionError):
    def __init__(self, service: type):
        super().__init__(f"service '{service.__qualname__}' is already registered")


class CalledNonCallableError(DependencyInjectionError):
    def __init__(self, called: Any):
        super().__init__(f"{called} is not callable")
