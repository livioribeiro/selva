import warnings
from dataclasses import dataclass
from enum import IntEnum
from types import FunctionType, MethodType
from typing import Any, Callable, Dict, List, Optional, Union, get_type_hints
from weakref import finalize

from .errors import DependencyLoopError, IncompatibleTypesError, InvalidScopeError

InjectableType = Union[type, FunctionType, MethodType]

__all__ = ["Scope", "Container"]


class Scope(IntEnum):
    SINGLETON = 1
    DEPENDENT = 2
    TRANSIENT = 3


@dataclass
class ServiceDefinition:
    scope: Scope
    factory: Union[type, FunctionType, MethodType]

    def accept_scope(self, scope: Scope) -> bool:
        return self.scope <= scope


class Container:
    def __init__(self):
        self.registry: Dict[type, ServiceDefinition] = dict()
        self.store_singleton: Dict[type, Any] = dict()
        self.store_dependent: Dict[int, Dict[type, Any]] = dict()

    def singleton(self, service: InjectableType = None, *, provides: type = None):
        return self.register(Scope.SINGLETON, service, provides=provides)

    def dependent(self, service: InjectableType = None, *, provides: type = None):
        return self.register(Scope.DEPENDENT, service, provides=provides)

    def transient(self, service: InjectableType = None, *, provides: type = None):
        return self.register(Scope.TRANSIENT, service, provides=provides)

    def register(
        self, scope: Scope, service: InjectableType = None, *, provides: type = None
    ):
        def register_func(service):
            if isinstance(service, type):
                if provides and not issubclass(service, provides):
                    raise IncompatibleTypesError(service, provides)

                provided_service = provides or service
            elif isinstance(service, (FunctionType, MethodType)):
                if provides:
                    warnings.warn(
                        UserWarning(
                            "option 'provides' on a factory function has no effect"
                        )
                    )

                service_type = get_type_hints(service).get("return")
                if service_type is None:
                    raise ValueError("factory function must have a return type")
                provided_service = service_type

            self.registry[provided_service] = ServiceDefinition(scope, factory=service)
            return service

        return register_func(service) if service else register_func

    def _get_definition(self, service_type: type) -> Optional[ServiceDefinition]:
        return self.registry.get(service_type)

    def has(self, service_type: type, scope: Scope = None) -> bool:
        definition = self._get_definition(service_type)
        if not definition:
            return False

        if scope:
            return definition.scope == scope

        return True

    def get(self, service_type: type, *, context: Any = None) -> Any:
        return self._get(service_type, context)

    def _get(
        self,
        service_type: type,
        context: Any = None,
        valid_scope: Scope = None,
        stack: list = None,
    ) -> Any:
        definition = self._get_definition(service_type)
        if not definition:
            raise ValueError("service not found")

        if not valid_scope:
            valid_scope = definition.scope

        if not definition.accept_scope(valid_scope):
            requester = stack[0] if stack else None
            raise InvalidScopeError(
                service_type, definition.scope.name, valid_scope.name, requester
            )

        if not stack:
            stack = list()

        if service_type in stack:
            raise DependencyLoopError(stack + [service_type])
        else:
            stack.append(service_type)

        if definition.scope == Scope.SINGLETON:
            service = self.store_singleton.get(service_type)
            if not service:
                service = self._create_service(valid_scope, stack, definition)
                self.store_singleton[service_type] = service
        elif definition.scope == Scope.DEPENDENT:
            if context is None:
                raise ValueError("'context' is required for DEPENDENT scope")
            context_id = id(context)
            if context_id not in self.store_dependent:
                self.store_dependent[context_id] = dict()
                finalize(context, self.store_dependent.pop, context_id)

            service = self.store_dependent[context_id].get(service_type)
            if not service:
                service = self._create_service(valid_scope, stack, definition, context)
                self.store_dependent[context_id][service_type] = service
        else:
            service = self._create_service(valid_scope, stack, definition)

        return service

    def _create_service(
        self,
        valid_scope: Scope,
        stack: List[type],
        definition: ServiceDefinition,
        context: Any = None,
    ):
        factory = definition.factory

        if isinstance(factory, type):
            types = get_type_hints(factory.__init__)
        else:
            types = get_type_hints(factory)
            types.pop("return")

        params = {
            name: self._get(svc, context, valid_scope, stack)
            for name, svc in types.items()
        }

        return factory(**params)

    def call(
        self,
        func: Callable,
        *,
        context: Any = None,
        kwargs: Dict[str, Any] = None,
    ) -> Any:
        kwargs = kwargs or dict()

        types = get_type_hints(func)
        types.pop("return", None)

        params = {
            name: self.get(svc, context=context)
            for name, svc in types.items()
            if self.has(svc)
        }

        # kwargs takes precedence
        params.update(kwargs)

        return func(**params)
