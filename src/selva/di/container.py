import asyncio
import inspect
from collections.abc import AsyncGenerator, Awaitable, Generator, Iterable
from types import FunctionType, ModuleType
from typing import Any, TypeVar

import structlog

from selva._util.maybe_async import maybe_async
from selva._util.package_scan import scan_packages
from selva.di.decorator import ATTRIBUTE_DI_SERVICE
from selva.di.decorator import service as service_decorator
from selva.di.error import (
    DependencyLoopError,
    NonInjectableTypeError,
    ServiceNotFoundError,
    ServiceWithoutDecoratorError,
)
from selva.di.interceptor import Interceptor
from selva.di.service.model import InjectableType, ServiceDependency, ServiceSpec
from selva.di.service.parse import parse_service_spec
from selva.di.service.registry import ServiceRegistry

logger = structlog.get_logger(__name__)

T = TypeVar("T")


def _is_service(arg) -> bool:
    return (inspect.isfunction(arg) or inspect.isclass(arg)) and hasattr(
        arg, ATTRIBUTE_DI_SERVICE
    )


class Container:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.cache: dict[tuple[type, str | None], Any] = {}
        self.finalizers: list[Awaitable] = []
        self.interceptors: list[type[Interceptor]] = []

    def scan(self, *args: str | ModuleType):
        for item in scan_packages(*args, predicate=_is_service):
            self.register(item)

    def register(self, injectable: InjectableType):
        if not inspect.isfunction(injectable) and not inspect.isclass(injectable):
            raise NonInjectableTypeError(injectable)

        service_info = getattr(injectable, ATTRIBUTE_DI_SERVICE, None)

        if not service_info:
            raise ServiceWithoutDecoratorError(injectable)

        provides, name = service_info
        service_spec = parse_service_spec(injectable, provides, name)
        provided_service = service_spec.service

        self.registry[provided_service, name] = service_spec

        log_context = {
            "service": f"{injectable.__module__}.{injectable.__qualname__}",
        }

        if name:
            log_context["name"] = name

        if provides:
            log_context["provides"] = f"{provides.__module__}.{provides.__qualname__}"

        logger.debug("service registered", **log_context)

    def define(self, service_type: type, instance: Any, *, name: str = None):
        self.cache[service_type, name] = instance

        log_context = {
            "service": f"{service_type.__module__}.{service_type.__qualname__}"
        }

        if name:
            log_context["name"] = name

        logger.debug("service defined", **log_context)

    def interceptor(self, interceptor: type[Interceptor]):
        self.register(
            service_decorator(
                interceptor,
                provides=Interceptor,
                name=f"{interceptor.__module__}.{interceptor.__qualname__}",
            )
        )
        self.interceptors.append(interceptor)

        logger.debug(
            "interceptor registered",
            interceptor=f"{interceptor.__module__}.{interceptor.__qualname__}",
        )

    def has(self, service_type: type, name: str = None) -> bool:
        definition = self.registry.get(service_type, name=name)
        return definition is not None

    def iter_service(
        self, service_type: type
    ) -> Iterable[tuple[type | FunctionType, str | None]]:
        record = self.registry.services.get(service_type)
        if not record:
            raise ServiceNotFoundError(service_type)

        for name, definition in record.providers.items():
            yield definition.impl, name

    def iter_all_services(
        self,
    ) -> Iterable[tuple[type, type | FunctionType | None, str | None]]:
        for _interface, record in self.registry.services.items():
            for name, definition in record.providers.items():
                yield definition.service, definition.impl, name

    async def get(
        self, service_type: type[T], *, name: str = None, optional=False
    ) -> T:
        dependency = ServiceDependency(service_type, name=name, optional=optional)
        return await self._get(dependency)

    async def run_finalizers(self):
        for finalizer in reversed(self.finalizers):
            await finalizer

        self.finalizers.clear()

    def _get_from_cache(self, service_type: type[T], name: str | None) -> T | None:
        return self.cache.get((service_type, name))

    async def _get(
        self,
        dependency: ServiceDependency,
        stack: list[tuple[type, str | None]] = None,
    ) -> Any | None:
        service_type, service_name, optional = (
            dependency.service,
            dependency.name,
            dependency.optional,
        )

        # check if service exists in cache
        if instance := self._get_from_cache(service_type, service_name):
            return instance

        try:
            service_spec = self.registry.get(service_type, service_name)
            if not service_spec:
                raise ServiceNotFoundError(service_type, service_name)
        except ServiceNotFoundError:
            if optional:
                return None
            raise

        stack = stack or []

        if (service_type, service_name) in stack:
            raise DependencyLoopError(stack, (service_type, service_name))

        stack.append((service_type, service_name))
        instance = await self._create_service(service_spec, stack)
        stack.pop()

        return instance

    async def _get_dependent_services(
        self, service_spec: ServiceSpec, stack: list
    ) -> dict[str, Any]:
        return {
            name: await self._get(dep, stack) for name, dep in service_spec.dependencies
        }

    async def _create_service(
        self,
        service_spec: ServiceSpec,
        stack: list[tuple[type[T], str]],
    ) -> T:
        name = service_spec.name

        if factory := service_spec.factory:
            dependencies = await self._get_dependent_services(service_spec, stack)

            instance = await maybe_async(factory, **dependencies)
            if inspect.isgenerator(instance):
                generator = instance
                instance = await asyncio.to_thread(next, generator)
                self._setup_generator_finalizer(generator)
            elif inspect.isasyncgen(instance):
                generator = instance
                instance = await anext(generator)
                self._setup_asyncgen_finalizer(generator)

            self.cache[service_spec.service, name] = instance
        else:
            instance = service_spec.impl()
            self.cache[service_spec.service, name] = instance

            dependencies = await self._get_dependent_services(service_spec, stack)

            for name, dep_service in dependencies.items():
                setattr(instance, name, dep_service)

            if initializer := service_spec.initializer:
                await maybe_async(initializer, instance)

            self._setup_finalizer(service_spec, instance)

        if service_spec.service is not Interceptor:
            await self._run_interceptors(instance, service_spec.service)

        return instance

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
