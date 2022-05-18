import asyncio
import inspect
from asyncio import AbstractEventLoop
from collections.abc import Callable
from concurrent.futures import Executor, ThreadPoolExecutor
from functools import partial
from types import ModuleType
from typing import Any, Optional, Union
from weakref import finalize

from .decorators import DEPENDENCY_ATRIBUTE
from .errors import (
    CalledNonCallableError,
    DependencyLoopError,
    InvalidScopeError,
    MissingDependentContextError,
)
from .scan import scan_packages
from .service.model import InjectableType, Scope, ServiceDefinition, ServiceDependency
from .service.parse import get_dependencies, parse_definition
from .service.registry import ServiceRegistry


class Container:
    def __init__(self, loop: AbstractEventLoop = None, executor: Executor = None):
        self.registry = ServiceRegistry()
        self.store_singleton: dict[type, Any] = {}
        self.store_dependent: dict[int, dict[type, Any]] = {}
        self.loop = loop or asyncio.get_running_loop()
        self.executor = executor or ThreadPoolExecutor()

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

    def scan(self, *packages: Union[str, ModuleType]):
        for service in scan_packages(*packages):
            scope, provides, name = getattr(service, DEPENDENCY_ATRIBUTE)
            self.register(service, scope, provides=provides, name=name)

    def has(self, service_type: type, scope: Scope = None) -> bool:
        definition = self.registry.get(service_type, optional=True)
        if not definition:
            return False

        if scope:
            return definition.scope == scope

        return True

    async def get(
        self, service_type: type, *, context: Any = None, name: str = None
    ) -> Any:
        instance = await self._get(ServiceDependency(service_type, name=name), context)

        initializer = getattr(instance, "initialize", None)

        if inspect.ismethod(initializer):
            dependencies = await self._resolve_dependencies(initializer, context)
            if inspect.iscoroutinefunction(initializer):
                await initializer(**dependencies)
            else:
                await self.loop.run_in_executor(self.executor, partial(initializer, **dependencies))

        return instance

    async def _resolve_dependencies(self, service: InjectableType, context: Any = None):
        return {
            name: await self._get(dep, context)
            for name, dep in get_dependencies(service)
        }

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

        stack = stack or list()

        if service_type in stack:
            raise DependencyLoopError(stack + [service_type])

        stack.append(service_type)

        if definition.scope == Scope.SINGLETON:
            service = self.store_singleton.get(service_type)
            if not service:
                service = await self._create_service(definition, valid_scope, stack)
                self.store_singleton[service_type] = service
        elif definition.scope == Scope.DEPENDENT:
            if context is None:
                raise MissingDependentContextError()
            context_id = id(context)
            if context_id not in self.store_dependent:
                self.store_dependent[context_id] = dict()
                finalize(context, self.store_dependent.pop, context_id)

            service = self.store_dependent[context_id].get(service_type)
            if not service:
                service = await self._create_service(
                    definition, valid_scope, stack, context
                )
                self.store_dependent[context_id][service_type] = service
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

        return await self.loop.run_in_executor(
            self.executor, partial(factory, **dependencies)
        )

    async def call(
        self,
        callable_obj: Callable,
        *,
        context: Any = None,
        args: list[Any] = None,
        kwargs: dict[str, Any] = None,
    ) -> Any:
        args = args or list()
        kwargs = kwargs or dict()

        if not callable(callable_obj):
            raise CalledNonCallableError(callable_obj)

        if inspect.isfunction(callable_obj):
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

        return await self.loop.run_in_executor(
            self.executor, partial(func, *func_args.args, **func_args.kwargs)
        )
