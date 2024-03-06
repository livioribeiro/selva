import asyncio
import inspect
from collections.abc import AsyncGenerator, Awaitable, Generator, Iterable
from types import FunctionType, ModuleType
from typing import Any, Type, TypeVar

from asgikit.requests import Request

from loguru import logger

from selva._util.maybe_async import maybe_async
from selva._util.package_scan import scan_packages
from selva.di.decorator import DI_ATTRIBUTE_SERVICE, DI_ATTRIBUTE_RESOURCE, service
from selva.di.error import (
    DependencyLoopError,
    ServiceNotFoundError,
    ServiceWithoutDecoratorError,
    NonInjectableTypeError
)
from selva.di.inspect import is_service, is_resource
from selva.di.interceptor import Interceptor
from selva.di.service.model import InjectableType, ResourceInfo, ServiceDependency, ServiceInfo, ServiceSpec
from selva.di.service.parse import get_dependencies, parse_service_spec
from selva.di.service.registry import ServiceRegistry

T = TypeVar("T")


class Container:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.store: dict[tuple[type, str | None], Any] = {}
        self.finalizers: list[Awaitable] = []
        self.startup: list[tuple[Type, str | None]] = []
        self.interceptors: list[Type[Interceptor]] = []
        self.resource_registry = ServiceRegistry()
        self.resource_finalizers: dict[Request, list[Awaitable]] = {}

    def register(self, injectable: InjectableType):
        if service_info := getattr(injectable, DI_ATTRIBUTE_SERVICE, None):
            self._register_service_spec(injectable, service_info)
        elif resource_info := getattr(injectable, DI_ATTRIBUTE_RESOURCE, None):
            self._register_resource_spec(injectable, resource_info)
        elif inspect.isfunction(injectable) or inspect.isclass(injectable):
            raise ServiceWithoutDecoratorError(injectable)
        else:
            raise NonInjectableTypeError(injectable)

    def _register_service_spec(
        self, injectable: InjectableType, info: ServiceInfo
    ):
        provides, name, startup = info
        service_spec = parse_service_spec(injectable, provides, name)
        provided_service = service_spec.provides

        self.registry[provided_service, name] = service_spec

        if startup:
            self.startup.append((service_spec.provides, name))

        if provides:
            logger.trace(
                "service registered: {}.{}; provides={}.{} name={}",
                injectable.__module__,
                injectable.__qualname__,
                provides.__module__,
                provides.__qualname__,
                name or "",
            )
        else:
            logger.trace(
                "service registered: {}.{}; name={}",
                injectable.__module__,
                injectable.__qualname__,
                name or "",
            )

    def _register_resource_spec(
        self, injectable: InjectableType, info: ResourceInfo
    ):
        provides, name = info
        resource_spec = parse_service_spec(injectable, provides, name, True)
        provided_resource = resource_spec.provides

        self.resource_registry[provided_resource, name] = resource_spec

        if provides:
            logger.trace(
                "resource registered: {}.{}; provideds={}.{} name={}",
                injectable.__module__,
                injectable.__qualname__,
                provides.__module__,
                provides.__qualname__,
                name or "",
            )
        else:
            logger.trace(
                "resource registered: {}.{}; name={}",
                injectable.__module__,
                injectable.__qualname__,
                name or "",
            )

    def define(self, service_type: type, instance: Any, *, name: str = None):
        self.store[service_type, name] = instance

        logger.trace(
            "service defined: {}; name={}", service_type.__qualname__, name or ""
        )

    def interceptor(self, interceptor: Type[Interceptor]):
        self.register(
            service(
                interceptor,
                provides=Interceptor,
                name=f"{interceptor.__module__}.{interceptor.__qualname__}",
            )
        )
        self.interceptors.append(interceptor)

        logger.trace("interceptor registered: {}", interceptor.__qualname__)

    def scan(self, *packages: str | ModuleType):
        def predicate_services(item: Any):
            return hasattr(item, DI_ATTRIBUTE_SERVICE)

        for found_service in scan_packages(packages, predicate_services):
            self.register(found_service)

    def has(self, service_type: type, name: str = None) -> bool:
        definition = self.registry.get(service_type, name=name)
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

    async def get(self, service_type: T, *, name: str = None, optional=False) -> T:
        dependency = ServiceDependency(service_type, name=name, optional=optional)
        return await self._get(dependency)

    async def create(self, service_type: type) -> Any:
        instance = service()
        for name, dep_spec in get_dependencies(service_type):
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

        # check if service exists in cache
        if instance := self._get_from_cache(service_type, name):
            return instance

        try:
            service_spec = self.registry.get(service_type, name) or self.resource_registry.get(service_type, name)
            if not service_spec:
                raise ServiceNotFoundError(service_type, name)
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
        name = service_spec.name

        # check if service exists in cache
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

            # if the service is not a resource, cache it
            if not service_spec.resource:
                self.store[service_spec.provides, name] = instance
        else:
            instance = service_spec.service()

            # if the service is not a resource, cache it
            if not service_spec.resource:
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

    async def _run_startup(self):
        for service, name in self.startup:
            await self.get(service, name=name)

    async def _run_finalizers(self, request: Request = None):
        if request:
            finalizers = self.resource_finalizers[request]
        else:
            finalizers = self.finalizers

        for finalizer in reversed(finalizers):
            await finalizer

        finalizers.clear()
