import asyncio
import inspect
import weakref
from collections.abc import Callable
from types import ModuleType
from typing import Any, Optional, Union

from selva.utils.package_scan import scan_packages

from .decorators import DEPENDENCY_ATTRIBUTE
from .errors import (
    CalledNonCallableError,
    DependencyLoopError,
    InvalidScopeError,
    MissingDependentContextError,
    ServiceNotRegisteredError,
)
from .service.model import InjectableType, Scope, ServiceDefinition, ServiceDependency
from .service.parse import get_dependencies, parse_definition
from .service.registry import ServiceRegistry

INITIALIZE_METHOD_NAME = "initialize"


class Container:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.store_singleton: dict[type, Any] = {}
        self.store_dependent: dict[int, dict[type, Any]] = {}

    def register(
        self,
        service: InjectableType,
        scope: Scope,
        *,
        provides: type = None,
        name: str = None,
    ):
        definition = parse_definition(service, scope, provides)
        provided_service = definition.provides
        self.registry[provided_service, name] = definition

    def register_singleton(
        self,
        service: InjectableType,
        *,
        provides: type = None,
        name: str = None,
    ):
        self.register(service, Scope.SINGLETON, provides=provides, name=name)

    def register_dependent(
        self,
        service: InjectableType,
        *,
        provides: type = None,
        name: str = None,
    ):
        self.register(service, Scope.DEPENDENT, provides=provides, name=name)

    def register_transient(
        self,
        service: InjectableType,
        *,
        provides: type = None,
        name: str = None,
    ):
        self.register(service, Scope.TRANSIENT, provides=provides, name=name)

    def define_singleton(self, service_type: type, instance: object):
        if not self.has(service_type):
            self.register(service_type, Scope.SINGLETON)

        self.store_singleton[service_type] = instance

    def define_dependent(self, service_type: type, instance: object, *, context: Any):
        if not self.has(service_type):
            raise ServiceNotRegisteredError(service_type)

        self._ensure_dependent_context(context)
        self.store_dependent[id(context)][service_type] = weakref.ref(instance)

    def scan(self, *packages: Union[str, ModuleType]):
        def predicate(item: Any):
            return (inspect.isfunction(item) or inspect.isclass(item)) and hasattr(
                item, DEPENDENCY_ATTRIBUTE
            )

        for service in scan_packages(packages, predicate):
            scope, provides, name = getattr(service, DEPENDENCY_ATTRIBUTE)
            self.register(service, scope, provides=provides, name=name)

    def has(self, service: type, scope: Scope = None) -> bool:
        definition = self.registry.get(service, optional=True)

        if not definition:
            return False

        if scope:
            return definition.scope == scope

        return True

    async def get(
        self, service_type: type, *, context: Any = None, name: str = None
    ) -> Any:
        # try getting from singleton store
        instance = self.store_singleton.get(service_type)

        # then try from the dependent store
        if instance is None and context in self.store_dependent:
            instance = self.store_dependent[context].get(service_type)

        # else create new instance
        if instance is None:
            instance = await self._get(
                ServiceDependency(service_type, name=name), context
            )

        initializer = getattr(instance, INITIALIZE_METHOD_NAME, None)
        if inspect.ismethod(initializer):
            dependencies = await self._resolve_dependencies(initializer, context)
            if inspect.iscoroutinefunction(initializer):
                await initializer(**dependencies)
            else:
                await asyncio.to_thread(initializer, **dependencies)

        return instance

    async def _resolve_dependencies(self, service: InjectableType, context: Any = None):
        return {
            name: await self._get(dep, context)
            for name, dep in get_dependencies(service)
        }

    def _ensure_dependent_context(self, context: Any):
        # Make sure the dependent store exists for the given context and set finalizer
        if context is None:
            raise MissingDependentContextError()

        context_id = id(context)
        if context_id not in self.store_dependent:
            self.store_dependent[context_id] = {}
            weakref.finalize(context, self.store_dependent.pop, context_id, None)

    async def _get(
        self,
        dependency: ServiceDependency,
        context: Any = None,
        valid_scope: Scope = None,
        stack: list = None,
    ) -> Optional[Any]:
        service_type, name = dependency.service, dependency.name
        definition = self.registry.get(service_type, name, dependency.optional)

        if definition is None:
            return None

        valid_scope = valid_scope or definition.scope

        if not definition.accept_scope(valid_scope):
            requester = stack[0] if stack else None
            raise InvalidScopeError(
                service_type, definition.scope.name, valid_scope.name, requester
            )

        stack = stack or []

        if service_type in stack:
            raise DependencyLoopError(stack + [service_type])

        stack.append(service_type)

        if definition.scope == Scope.SINGLETON:
            service = self.store_singleton.get(service_type)
            if not service:
                service = await self._create_service(definition, valid_scope, stack)
                self.store_singleton[service_type] = service
        elif definition.scope == Scope.DEPENDENT:
            context_id = id(context)
            self._ensure_dependent_context(context)

            service = self.store_dependent[context_id].get(service_type)

            if not service:
                service = await self._create_service(
                    definition, valid_scope, stack, context
                )
                self.store_dependent[context_id][service_type] = weakref.ref(service)
            else:
                # get out of weakref.ref
                service = service()
        else:
            service = await self._create_service(definition, valid_scope, stack)

        return service

    async def create(self, service: type, *, context: Any = None) -> Any:
        dependencies = {
            name: (await self._get(dep, context, Scope.TRANSIENT))
            for name, dep in get_dependencies(service)
        }
        return service(**dependencies)

    async def _create_service(
        self,
        definition: ServiceDefinition,
        valid_scope: Scope,
        stack: list[type],
        context: Any = None,
    ) -> Any:
        factory = definition.factory

        dependencies = {
            name: await self._get(dep, context, valid_scope, stack)
            for name, dep in definition.dependencies
        }

        if inspect.iscoroutinefunction(factory):
            return await factory(**dependencies)

        return await asyncio.to_thread(factory, **dependencies)

    async def call(
        self,
        callable_obj: Callable,
        *,
        context: Any = None,
        args: tuple[Any, ...] = None,
        kwargs: dict[str, Any] = None,
    ) -> Any:
        args = args or []
        kwargs = kwargs or {}

        if not callable(callable_obj):
            raise CalledNonCallableError(callable_obj)

        if inspect.isfunction(callable_obj) or inspect.ismethod(callable_obj):
            func = callable_obj
        else:
            func = callable_obj.__call__

        params = {
            name: await self._get(dep, context=context)
            for name, dep in get_dependencies(func)
            if self.has(dep.service)
        }

        params.update(kwargs)

        func_args = inspect.signature(func).bind(*args, **params)
        func_args.apply_defaults()

        if inspect.iscoroutinefunction(func):
            return await func(*func_args.args, **func_args.kwargs)

        return await asyncio.to_thread(func, *func_args.args, **func_args.kwargs)
