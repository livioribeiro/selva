import functools
from collections import defaultdict
from collections.abc import Callable
from types import ModuleType
from typing import Any, Type, TypeVar

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
from .interceptor import Interceptor
from .service.model import InjectableType, Scope, ServiceDefinition, ServiceDependency
from .service.parse import get_dependencies, parse_definition
from .service.registry import ServiceRegistry

TService = TypeVar("TService")


class Container:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.store_singleton: dict[tuple[type, str | None], Any] = {}
        self.store_dependent: dict[
            int, dict[tuple[type, str | None], Any]
        ] = defaultdict(dict)
        self.finalizers: dict[int | None, list[Callable]] = defaultdict(list)
        self.interceptors: list[Type[Interceptor]] = []

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

    def define_singleton(self, service_type: type, instance: Any, *, name: str = None):
        self.store_singleton[service_type, name] = instance

    def define_dependent(
        self, service_type: type, instance: Any, *, context: Any, name: str = None
    ):
        if context is None:
            raise MissingDependentContextError()

        if not self.has(service_type, Scope.DEPENDENT):

            def defined_only_factory() -> service_type:
                raise InstanceNotDefinedError(service_type)

            self.register(defined_only_factory, scope=Scope.DEPENDENT)

        self.store_dependent[id(context)][service_type, name] = instance

    def interceptor(self, interceptor: Type[Interceptor]):
        self.register(
            interceptor,
            provides=Interceptor,
            name=f"{interceptor.__module__}.{interceptor.__qualname__}",
        )
        self.interceptors.append(interceptor)

    def scan(self, *packages: str | ModuleType):
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

    def _get_from_cache(
        self, service_type: type, name: str | None, context: Any = None
    ) -> Any | None:
        # try getting from singleton store
        if instance := self.store_singleton.get((service_type, name)):
            return instance

        # try from the dependent store
        if store := self.store_dependent.get(id(context)):
            if instance := store.get((service_type, name)):
                return instance

        return None

    async def _get(
        self,
        dependency: ServiceDependency,
        context: Any = None,
        valid_scope: Scope = None,
        stack: list = None,
    ) -> Any | None:
        service_type, name = dependency.service, dependency.name

        if instance := self._get_from_cache(service_type, name, context):
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
        instance = await self._create_service(
            definition, valid_scope, stack, name, context
        )
        stack.pop()

        return instance

    async def _create_service(
        self,
        definition: ServiceDefinition,
        valid_scope: Scope,
        stack: list[type],
        name: str = None,
        context: Any = None,
    ) -> Any:
        factory = definition.factory

        dependencies = {
            name: await self._get(dep, context, valid_scope, stack)
            for name, dep in definition.dependencies
        }

        # check if service have been created from initializers
        if instance := self._get_from_cache(definition.provides, name, context):
            return instance

        instance = await maybe_async(factory, **dependencies)

        match definition.scope:
            case Scope.SINGLETON:
                self.store_singleton[definition.provides, name] = instance
            case Scope.DEPENDENT:
                self.store_dependent[id(context)][definition.provides, name] = instance

        await self._run_initializer(definition, instance, context)
        await self._setup_finalizer(definition, instance, context)

        if definition.provides is not Interceptor:
            await self._run_interceptors(instance, definition.provides)

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

    async def _run_interceptors(self, instance: Any, service_type: type):
        for cls in self.interceptors:
            interceptor = await self.get(
                Interceptor, name=f"{cls.__module__}.{cls.__qualname__}"
            )
            await maybe_async(interceptor.intercept, instance, service_type)

    async def run_finalizers(self, context=None):
        context_id = id(context) if context else None

        for finalizer in reversed(self.finalizers[context_id]):
            await maybe_async(finalizer)

        self.finalizers.pop(context_id, None)

        if context_id:
            self.store_dependent.pop(context_id, None)
