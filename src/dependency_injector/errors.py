from typing import List


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
