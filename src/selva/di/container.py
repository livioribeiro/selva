import functools
from collections import defaultdict
from collections.abc import Callable
from types import ModuleType
from typing import Any, Optional, TypeVar, Union

from selva.utils.maybe_async import maybe_async
from selva.utils.package_scan import scan_packages

from .decorators import DI_SERVICE_ATTRIBUTE
from .errors import (
    DependencyLoopError,
    InstanceNotDefinedError,
    InvalidScopeError,
    MissingDependentContextError,
    ServiceNotFoundError,
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
        self.store_dependent: dict[int, dict[type, Any]] = defaultdict(dict)
        self.finalizers: dict[int | None, list[Callable]] = defaultdict(list)

    def register(
        self,
        service: InjectableType,
        scope=Scope.SINGLETON,
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

    def define_singleton(self, service_type: type, instance: Any):
        self.store_singleton[service_type] = instance

    def define_dependent(self, service_type: type, instance: Any, *, context: Any):
        if context is None:
            raise MissingDependentContextError()

        if not self.has(service_type, Scope.DEPENDENT):

            def defined_only_factory() -> service_type:
                raise InstanceNotDefinedError(service_type)

            self.register(defined_only_factory, scope=Scope.DEPENDENT)

        # service = weakref.proxy(instance) if instance is context else instance
        self.store_dependent[id(context)][service_type] = instance

    def scan(self, *packages: Union[str, ModuleType]):
        def predicate(item: Any):
            return hasattr(item, DI_SERVICE_ATTRIBUTE)

        for service in scan_packages(packages, predicate):
            scope, provides, name = getattr(service, DI_SERVICE_ATTRIBUTE)
            self.register(service, scope, provides=provides, name=name)

    def has(self, service: type, scope: Scope = None) -> bool:
        definition = self.registry.get(service)

        if not definition:
            return False

        if scope:
            return definition.scope == scope

        return True

    async def get(
        self,
        service_type: TService,
        *,
        context: Any = None,
        name: str = None,
        optional=False,
    ) -> TService:
        dependency = ServiceDependency(service_type, name=name, optional=optional)
        return await self._get(dependency, context)

    async def create(self, service: type, *, context: Any = None) -> Any:
        dependencies = await self._resolve_dependencies(service, context)
        instance = service(**dependencies)
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

        # try getting from singleton store
        if instance := self.store_singleton.get(service_type):
            return instance

        # try from the dependent store
        if (store := self.store_dependent.get(id(context))) and (
            instance := store.get(service_type)
        ):
            return instance

        try:
            definition = self.registry[service_type, name]
        except ServiceNotFoundError:
            if dependency.optional:
                return None
            raise

        valid_scope = valid_scope or definition.scope

        if not definition.accept_scope(valid_scope):
            requester = stack[0] if stack else None
            raise InvalidScopeError(
                service_type, definition.scope.name, valid_scope.name, requester
            )

        if definition.scope is Scope.DEPENDENT and context is None:
            raise MissingDependentContextError()

        stack = stack or []

        if service_type in stack:
            raise DependencyLoopError(stack + [service_type])

        stack.append(service_type)

        instance = await self._create_service(definition, valid_scope, stack, context)

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

        instance = await maybe_async(factory, **dependencies)

        match definition.scope:
            case Scope.SINGLETON:
                self.store_singleton[definition.provides] = instance
            case Scope.DEPENDENT:
                self.store_dependent[id(context)][definition.provides] = instance

        await self._run_initializer(definition, instance, context)
        await self._setup_finalizer(definition, instance, context)

        return instance

    async def _run_initializer(
        self, definition: ServiceDefinition, instance: Any, context: Any | None
    ):
        initializer = definition.initializer

        if initializer is None:
            return

        dependencies = await self._resolve_dependencies(initializer, context)
        await maybe_async(initializer, instance, **dependencies)

    async def _setup_finalizer(
        self, definition: ServiceDefinition, instance: Any, context: Any | None
    ):
        finalizer = definition.finalizer

        if finalizer is None:
            return

        finalizer_key = None if definition.scope is Scope.SINGLETON else id(context)
        self.finalizers[finalizer_key].append(functools.partial(finalizer, instance))

    async def run_finalizers(self, context=None):
        context_id = id(context) if context else None

        for finalizer in self.finalizers[context_id]:
            await maybe_async(finalizer)

        self.finalizers.pop(context_id, None)

        if context_id:
            self.store_dependent.pop(context_id, None)
