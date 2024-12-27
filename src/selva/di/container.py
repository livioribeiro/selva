import asyncio
import inspect
from collections.abc import AsyncGenerator, Awaitable, Generator, Iterable
from types import FunctionType, ModuleType
from typing import Any, Type, TypeVar

import structlog

from selva._util.maybe_async import maybe_async
from selva._util.package_scan import scan_packages
from selva.di.decorator import DI_ATTRIBUTE_SERVICE
from selva.di.decorator import service as service_decorator
from selva.di.error import (
    NonInjectableTypeError,
    ServiceNotFoundError,
    ServiceWithoutDecoratorError, DependencyLoopError,
)
from selva.di.interceptor import Interceptor
from selva.di.lazy import Lazy
from selva.di.locator import Locator
from selva.di.service.model import InjectableType, ServiceSpec
from selva.di.service.parse import parse_service_spec
from selva.di.service.registry import ServiceRegistry

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class Container:
    def __init__(self):
        self.registry = ServiceRegistry()
        self.store: dict[tuple[type, str | None], Any] = {}
        self.finalizers: list[Awaitable] = []
        self.startup: list[tuple[type, str | None]] = []
        self.interceptors: list[Type[Interceptor]] = []

    def register(self, injectable: InjectableType):
        service_info = getattr(injectable, DI_ATTRIBUTE_SERVICE, None)

        if not service_info:
            if inspect.isfunction(injectable):
                raise ServiceWithoutDecoratorError(injectable)

            raise NonInjectableTypeError(injectable)

        name, startup = service_info
        service_spec = parse_service_spec(injectable, name)
        provided_service = service_spec.provides

        self.registry[provided_service, name] = service_spec

        if startup:
            self.startup.append((service_spec.provides, name))

        log_context = {
            "service": f"{injectable.__module__}.{injectable.__qualname__}",
        }

        if name:
            log_context["name"] = name

        if provided_service:
            log_context["provides"] = f"{provided_service.__module__}.{provided_service.__qualname__}"

        logger.debug("service registered", **log_context)

    def define(self, service_type: type, instance: Any, *, name: str = None):
        self.store[service_type, name] = instance

        log_context = {
            "service": f"{service_type.__module__}.{service_type.__qualname__}"
        }

        if name:
            log_context["name"] = name

        logger.debug("service defined", **log_context)

    def interceptor(self, interceptor: Type[Interceptor]):
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
            yield definition.provides, name

    def iter_all_services(
        self,
    ) -> Iterable[tuple[type, type | FunctionType | None, str | None]]:
        for interface, record in self.registry.services.items():
            for name, definition in record.providers.items():
                yield interface, definition.provides, name

    async def get(
        self, service: Type[T], name: str = None, *, optional=False, locator=None, stack=None
    ) -> T:
        if not locator:
            locator = Locator(self)

        return await self._get(locator, service, name, optional, stack or [])

    def _get_from_cache(self, service_type: Type[T], name: str | None) -> T | None:
        return self.store.get((service_type, name))

    async def _get(
        self,
        locator: Locator,
        service_type: Type[T],
        name: str | None,
        optional: bool,
        stack: list[tuple[Type[T], str]],
    ) -> T | None:
        # check if service exists in cache
        if instance := self._get_from_cache(service_type, name):
            return instance

        if (service_type, name) in stack:
            raise DependencyLoopError(stack, (service_type, name))

        try:
            service_spec = self.registry.get(service_type, name)
            if not service_spec:
                raise ServiceNotFoundError(service_type, name)
        except ServiceNotFoundError:
            if optional:
                return None
            raise

        stack.append((service_type, name))
        instance = await self._create_service(service_spec, locator)
        stack.pop()

        return instance

    async def _create_service(
        self,
        service_spec: ServiceSpec,
        locator: Locator,
    ) -> Any:
        name = service_spec.name
        factory = service_spec.factory
        receives_locator = service_spec.receives_locator

        if inspect.iscoroutinefunction(factory):
            instance = await (factory(locator) if receives_locator else factory())
        elif inspect.isasyncgenfunction(factory):
            generator = factory(locator) if receives_locator else factory()
            instance = await anext(generator)
            self._setup_asyncgen_finalizer(generator)
        elif inspect.isgeneratorfunction(factory):
            generator = factory()
            instance = next(generator)
            self._setup_generator_finalizer(generator)
        else:
            instance = factory()

        self.store[service_spec.provides, name] = instance

        if service_spec.provides is not Interceptor:
            await self._run_interceptors(instance, service_spec.provides)

        return instance

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

    async def _run_finalizers(self):
        for finalizer in reversed(self.finalizers):
            await finalizer

        self.finalizers.clear()
