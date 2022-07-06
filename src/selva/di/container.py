from collections.abc import Awaitable
from types import ModuleType
from typing import Any, Type, TypeVar

from selva.utils.maybe_async import maybe_async
from selva.utils.package_scan import scan_packages

from .decorators import DI_SERVICE_ATTRIBUTE
from .errors import (
    DependencyLoopError,
    ServiceNotFoundError,
    ServiceWithoutDecoratorError,
)
from .interceptor import Interceptor
from .service.model import InjectableType, ServiceDefinition, ServiceDependency
from .service.parse import get_dependencies, parse_definition
from .service.registry import ServiceRegistry

TService = TypeVar("TService")


class Container:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.store: dict[tuple[type, str | None], Any] = {}
        self.finalizers: list[Awaitable] = []
        self.interceptors: list[Type[Interceptor]] = []

    def register(
        self,
        service: InjectableType,
        *,
        provides: type = None,
        name: str = None,
    ):
        definition = parse_definition(service, provides)
        provided_service = definition.provides
        self.registry[provided_service, name] = definition

    def service(self, service_type: type):
        service_info = getattr(service_type, DI_SERVICE_ATTRIBUTE, None)
        if not service_info:
            raise ServiceWithoutDecoratorError(service_type)

        provides, name = service_info
        self.register(service_type, provides=provides, name=name)

    def define_singleton(self, service_type: type, instance: Any, *, name: str = None):
        self.store[service_type, name] = instance

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
            provides, name = getattr(service, DI_SERVICE_ATTRIBUTE)
            self.register(service, provides=provides, name=name)

    def has(self, service: type) -> bool:
        definition = self.registry.get(service)
        return definition is not None

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

    def _get_from_cache(self, service_type: type, name: str | None) -> Any | None:
        # try getting from singleton store
        if instance := self.store.get((service_type, name)):
            return instance

        return None

    async def _get(
        self,
        dependency: ServiceDependency,
        context: Any = None,
        stack: list = None,
    ) -> Any | None:
        service_type, name = dependency.service, dependency.name

        if instance := self._get_from_cache(service_type, name):
            return instance

        try:
            definition = self.registry[service_type, name]
        except ServiceNotFoundError:
            if dependency.optional:
                return None
            raise

        stack = stack or []

        if service_type in stack:
            raise DependencyLoopError(stack + [service_type])

        stack.append(service_type)
        instance = await self._create_service(definition, stack, name, context)
        stack.pop()

        return instance

    async def _create_service(
        self,
        definition: ServiceDefinition,
        stack: list[type],
        name: str = None,
        context: Any = None,
    ) -> Any:
        factory = definition.factory

        dependencies = {
            name: await self._get(dep, context, stack)
            for name, dep in definition.dependencies
        }

        # check if service have been created from initializers
        if instance := self._get_from_cache(definition.provides, name):
            return instance

        instance = await maybe_async(factory, **dependencies)

        self.store[definition.provides, name] = instance

        await self._run_initializer(definition, instance)
        self._setup_finalizers(definition, instance)

        if definition.provides is not Interceptor:
            await self._run_interceptors(instance, definition.provides)

        return instance

    async def _run_initializer(self, definition: ServiceDefinition, instance: Any):
        for initializer in definition.initializers:
            dependencies = await self._resolve_dependencies(initializer)
            await maybe_async(initializer, instance, **dependencies)

    def _setup_finalizers(self, definition: ServiceDefinition, instance: Any):
        for finalizer in definition.finalizers:
            self.finalizers.append(maybe_async(finalizer, instance))

    async def _run_interceptors(self, instance: Any, service_type: type):
        for cls in self.interceptors:
            interceptor = await self.get(
                Interceptor, name=f"{cls.__module__}.{cls.__qualname__}"
            )
            await maybe_async(interceptor.intercept, instance, service_type)

    async def run_finalizers(self):
        for finalizer in reversed(self.finalizers):
            await finalizer

        self.finalizers.clear()
