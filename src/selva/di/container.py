import asyncio
import copy
import functools
import inspect
import weakref
from collections.abc import Callable
from types import ModuleType
from typing import Any, Optional, TypeVar, Union

from selva.utils.package_scan import scan_packages

from .decorators import DI_SERVICE_ATTRIBUTE
from .errors import (
    CalledNonCallableError,
    DependencyLoopError,
    InvalidScopeError,
    MissingDependentContextError,
    ServiceWithoutDecoratorError,
)
from .service.model import InjectableType, Scope, ServiceDefinition, ServiceDependency
from .service.parse import get_dependencies, parse_definition
from .service.registry import ServiceRegistry

TService = TypeVar("TService")


class Container:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.store_singleton: dict[type, Any] = {}
        self.store_dependent: dict[int, dict[type, Any]] = {}
        self.finalizers: list[Callable] = []

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

    def service(self, service_type: type):
        service_info = getattr(service_type, DI_SERVICE_ATTRIBUTE, None)
        if not service_info:
            raise ServiceWithoutDecoratorError(service_type)

        scope, provides, name = service_info
        self.register(service_type, scope, provides=provides, name=name)

    def define_singleton(self, service_type: type, instance: object):
        self.store_singleton[service_type] = instance

    def define_dependent(self, service_type: type, instance: object, *, context: Any):
        self._ensure_dependent_context(context)

        service = weakref.proxy(instance) if instance is context else instance
        self.store_dependent[id(context)][service_type] = service

    def scan(self, *packages: Union[str, ModuleType]):
        def predicate(item: Any):
            return hasattr(item, DI_SERVICE_ATTRIBUTE)

        for service in scan_packages(packages, predicate):
            scope, provides, name = getattr(service, DI_SERVICE_ATTRIBUTE)
            self.register(service, scope, provides=provides, name=name)

    def has(self, service: type, scope: Scope = None) -> bool:
        definition = self.registry.get(service, optional=True)

        if not definition:
            return False

        if scope:
            return definition.scope == scope

        return True

    async def get(
        self, service_type: TService, *, context: Any = None, name: str = None
    ) -> TService:
        instance = await self._get(ServiceDependency(service_type, name=name), context)
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

        # try getting from singleton store
        if instance := self.store_singleton.get(service_type):
            return instance

        # try from the dependent store
        if instance := self.store_dependent.get(id(context), {}).get(service_type):
            return instance

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
            instance = self.store_singleton.get(service_type)
            if not instance:
                instance = await self._create_service(definition, valid_scope, stack)
                self.store_singleton[service_type] = instance
        elif definition.scope == Scope.DEPENDENT:
            context_id = id(context)
            self._ensure_dependent_context(context)

            instance = self.store_dependent[context_id].get(service_type)

            if not instance:
                instance = await self._create_service(
                    definition, valid_scope, stack, context
                )
                self.store_dependent[context_id][service_type] = instance
        else:
            instance = await self._create_service(definition, valid_scope, stack)

        await self.run_initializer(definition, instance, context)
        await self.setup_finalizer(definition, instance, definition.scope)

        return instance

    async def create(self, service: type, *, context: Any = None) -> Any:
        dependencies = await self._resolve_dependencies(service, context)
        instance = service(**dependencies)
        return instance

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

        if inspect.isclass(factory):
            instance = factory(**dependencies)
        elif inspect.iscoroutinefunction(factory):
            instance = await factory(**dependencies)
        else:
            instance = await asyncio.to_thread(factory, **dependencies)

        return instance

    async def run_initializer(
        self, definition: ServiceDefinition, instance: Any, context: Any | None
    ):
        initializer = definition.initializer

        if initializer is None:
            return

        dependencies = await self._resolve_dependencies(initializer, context)
        if inspect.iscoroutinefunction(initializer):
            await initializer(instance, **dependencies)
        else:
            await asyncio.to_thread(initializer, instance, **dependencies)

    async def setup_finalizer(
        self, definition: ServiceDefinition, instance: Any, scope: Scope
    ):
        finalizer = definition.finalizer

        if finalizer is None:
            return

        if scope == Scope.SINGLETON:
            self.finalizers.append(functools.partial(finalizer, instance))
            return

        loop = asyncio.get_running_loop()

        def run_finalizer(instance_copy):
            if inspect.iscoroutinefunction(finalizer):
                if loop.is_running():
                    loop.create_task(finalizer(instance_copy))
                else:
                    asyncio.new_event_loop().run_until_complete(
                        finalizer(instance_copy)
                    )
            else:
                finalizer(instance_copy)

        # run finalizer with a shallow copy of the instance to prevent the reference on
        # the finalizer to keep the object alive
        weakref.finalize(instance, run_finalizer, copy.copy(instance))

    async def run_singleton_finalizers(self):
        for finalizer in self.finalizers:
            if inspect.iscoroutinefunction(finalizer):
                await finalizer()
            else:
                await asyncio.to_thread(finalizer)

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

        params = {
            name: await self._get(dep, context=context)
            for name, dep in get_dependencies(callable_obj)
            if self.has(dep.service)
        }

        params.update(kwargs)

        func_args = inspect.signature(callable_obj).bind(*args, **params)
        func_args.apply_defaults()

        callable_is_async = inspect.iscoroutinefunction(
            callable_obj,
        ) or inspect.iscoroutinefunction(
            getattr(callable_obj, "__call__", None),
        )

        if callable_is_async:
            return await callable_obj(*func_args.args, **func_args.kwargs)

        return await asyncio.to_thread(
            callable_obj, *func_args.args, **func_args.kwargs
        )
