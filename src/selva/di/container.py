import asyncio
import inspect
from collections.abc import AsyncGenerator, Awaitable, Generator, Iterable
from types import FunctionType, ModuleType
from typing import Any, Type, TypeVar

from loguru import logger

from selva._util.maybe_async import maybe_async
from selva._util.package_scan import scan_packages
from selva.di.decorator import DI_SERVICE_ATTRIBUTE
from selva.di.error import (
    DependencyLoopError,
    ServiceNotFoundError,
    ServiceWithoutDecoratorError,
)
from selva.di.interceptor import Interceptor
from selva.di.service.model import InjectableType, ServiceDependency, ServiceSpec
from selva.di.service.parse import get_dependencies, parse_service_spec
from selva.di.service.registry import ServiceRegistry

T = TypeVar("T")


class Container:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.store: dict[tuple[type, str | None], Any] = {}
        self.finalizers: list[Awaitable] = []
        self.interceptors: list[Type[Interceptor]] = []

    def register(
        self, service: InjectableType, *, provides: type = None, name: str = None
    ):
        self._register_service_spec(service, provides, name)

    def service(self, service: type):
        service_info = getattr(service, DI_SERVICE_ATTRIBUTE, None)

        if not service_info:
            raise ServiceWithoutDecoratorError(service)

        provides, name = service_info
        self._register_service_spec(service, provides, name)

    def _register_service_spec(
        self, service: type, provides: type | None, name: str | None
    ):
        service_spec = parse_service_spec(service, provides, name)
        provided_service = service_spec.provides

        self.registry[provided_service, name] = service_spec

        if provides:
            logger.trace(
                "service registered: {}.{}; provided-by={}.{} name={}",
                provides.__module__,
                provides.__qualname__,
                service.__module__,
                service.__qualname__,
                name or "",
            )
        else:
            logger.trace(
                "service registered: {}.{}; name={}",
                service.__module__,
                service.__qualname__,
                name or "",
            )

    def define(self, service_type: type, instance: Any, *, name: str = None):
        self.store[service_type, name] = instance

        logger.trace(
            "service defined: {}; name={}", service_type.__qualname__, name or ""
        )

    def interceptor(self, interceptor: Type[Interceptor]):
        self.register(
            interceptor,
            provides=Interceptor,
            name=f"{interceptor.__module__}.{interceptor.__qualname__}",
        )
        self.interceptors.append(interceptor)

        logger.trace("interceptor registered: {}", interceptor.__qualname__)

    def scan(self, *packages: str | ModuleType):
        def predicate(item: Any):
            return hasattr(item, DI_SERVICE_ATTRIBUTE)

        for service in scan_packages(packages, predicate):
            provides, name = getattr(service, DI_SERVICE_ATTRIBUTE)
            self.register(service, provides=provides, name=name)

    def has(self, service: type) -> bool:
        definition = self.registry.get(service)
        return definition is not None

    def iter_service(
        self, key: type
    ) -> Iterable[tuple[type | FunctionType, str | None]]:
        record = self.registry.services.get(key)
        if not record:
            raise ServiceNotFoundError(key)

        for name, definition in record.providers.items():
            yield definition.service, name

    def iter_all_services(
        self,
    ) -> Iterable[tuple[type, type | FunctionType | None, str | None]]:
        for interface, record in self.registry.services.items():
            for name, definition in record.providers.items():
                yield interface, definition.service, name

    async def get(self, service: T, *, name: str = None, optional=False) -> T:
        dependency = ServiceDependency(service, name=name, optional=optional)
        return await self._get(dependency)

    async def create(self, service: type) -> Any:
        instance = service()
        for name, dep_spec in get_dependencies(service):
            dependency = await self._get(dep_spec)
            setattr(instance, name, dependency)

        return instance

    def _get_from_cache(self, service_type: type, name: str | None) -> Any | None:
        # try getting service from store
        if instance := self.store.get((service_type, name)):
            return instance

        return None

    async def _get(
        self,
        dependency: ServiceDependency,
        stack: list = None,
    ) -> Any | None:
        service_type, name = dependency.service, dependency.name

        if instance := self._get_from_cache(service_type, name):
            return instance

        try:
            service_spec = self.registry[service_type, name]
        except ServiceNotFoundError:
            if dependency.optional:
                return None
            raise

        stack = stack or []

        if service_type in stack:
            raise DependencyLoopError(stack + [service_type])

        stack.append(service_type)
        instance = await self._create_service(service_spec, stack)
        stack.pop()

        return instance

    async def _create_service(
        self,
        service_spec: ServiceSpec,
        stack: list[type],
    ) -> Any:
        # check if service exists in cache
        name = service_spec.name
        if instance := self._get_from_cache(service_spec.provides, name):
            return instance

        if factory := service_spec.factory:
            dependencies = {
                name: await self._get(dep, stack)
                for name, dep in service_spec.dependencies
            }

            instance = await maybe_async(factory, **dependencies)
            if inspect.isgenerator(instance):
                generator = instance
                instance = await asyncio.to_thread(next, generator)
                self._setup_generator_finalizer(generator)
            elif inspect.isasyncgen(instance):
                generator = instance
                instance = await anext(generator)
                self._setup_asyncgen_finalizer(generator)

            self.store[service_spec.provides, name] = instance
        else:
            instance = service_spec.service()
            self.store[service_spec.provides, name] = instance

            for name, dep_service in service_spec.dependencies:
                dependency = await self._get(dep_service, stack)
                setattr(instance, name, dependency)

            await self._run_initializer(service_spec, instance)
            self._setup_finalizer(service_spec, instance)

        if service_spec.provides is not Interceptor:
            await self._run_interceptors(instance, service_spec.provides)

        return instance

    @staticmethod
    async def _run_initializer(service_spec: ServiceSpec, instance: Any):
        if initializer := service_spec.initializer:
            await maybe_async(initializer, instance)

    def _setup_finalizer(self, service_spec: ServiceSpec, instance: Any):
        if finalizer := service_spec.finalizer:
            self.finalizers.append(maybe_async(finalizer, instance))

    def _setup_generator_finalizer(self, gen: Generator):
        self.finalizers.append(asyncio.to_thread(next, gen, None))

    def _setup_asyncgen_finalizer(self, gen: AsyncGenerator):
        self.finalizers.append(anext(gen, None))

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
