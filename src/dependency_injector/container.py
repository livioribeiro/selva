import asyncio
import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, get_type_hints
from weakref import finalize

from dependency_injector import decorators
from dependency_injector.errors import (
    DependencyLoopError,
    InvalidScopeError,
    MissingDependentContextError,
    UnknownServiceError,
)
from dependency_injector.scan import scan_packages
from dependency_injector.service import InjectableType, Scope, ServiceDefinition


class Container:
    def __init__(self):
        self.registry: Dict[type, ServiceDefinition] = dict()
        self.store_singleton: Dict[type, Any] = dict()
        self.store_dependent: Dict[int, Dict[type, Any]] = dict()
        self.executor = ThreadPoolExecutor()

    def register(self, service: InjectableType, scope: Scope, *, provides: type = None):
        decorators.register(service, scope=scope, provides=provides)
        service_definition = getattr(service, "__dependency_injector__")
        self.registry[service_definition.provides] = service_definition

    def scan_packages(self, *packages):
        self.registry.update(scan_packages(*packages))

    def _get_definition(self, service_type: type) -> Optional[ServiceDefinition]:
        return self.registry.get(service_type)

    def has(self, service_type: type, scope: Scope = None) -> bool:
        definition = self._get_definition(service_type)
        if not definition:
            return False

        if scope:
            return definition.scope == scope

        return True

    async def get(self, service_type: type, *, context: Any = None) -> Any:
        return await self._get(service_type, context)

    async def _get(
        self,
        service_type: type,
        context: Any = None,
        valid_scope: Scope = None,
        stack: list = None,
    ) -> Any:
        definition = self.registry.get(service_type)
        if not definition:
            raise UnknownServiceError(service_type)

        if not valid_scope:
            valid_scope = definition.scope

        if not definition.accept_scope(valid_scope):
            requester = stack[0] if stack else None
            raise InvalidScopeError(
                service_type, definition.scope.name, valid_scope.name, requester
            )

        if not stack:
            stack = list()

        if service_type in stack:
            raise DependencyLoopError(stack + [service_type])
        else:
            stack.append(service_type)

        if definition.scope == Scope.SINGLETON:
            service = self.store_singleton.get(service_type)
            if not service:
                service = await self._create_service(valid_scope, stack, definition)
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
                    valid_scope, stack, definition, context
                )
                self.store_dependent[context_id][service_type] = service
        else:
            service = await self._create_service(valid_scope, stack, definition)

        return service

    async def _create_service(
        self,
        valid_scope: Scope,
        stack: List[type],
        definition: ServiceDefinition,
        context: Any = None,
    ):
        factory = definition.factory

        types = get_type_hints(
            factory.__init__ if inspect.isclass(factory) else factory
        )
        types.pop("return", None)

        params = {
            name: await self._get(svc, context, valid_scope, stack)
            for name, svc in types.items()
        }

        if asyncio.iscoroutinefunction(factory):
            return await factory(**params)
        else:
            return await asyncio.wrap_future(self.executor.submit(factory, **params))

    async def call(
        self,
        func: Callable,
        *,
        context: Any = None,
        kwargs: Dict[str, Any] = None,
    ) -> Any:
        kwargs = kwargs or dict()

        types = get_type_hints(func)
        types.pop("return", None)

        params = {
            name: await self.get(svc, context=context)
            for name, svc in types.items()
            if self.has(svc)
        }

        params.update(kwargs)

        func_args = inspect.signature(func).bind(**params)
        func_args.apply_defaults()

        if asyncio.iscoroutinefunction(func):
            return await func(*func_args.args, **func_args.kwargs)
        else:
            return await asyncio.wrap_future(
                self.executor.submit(func, *func_args.args, **func_args.kwargs)
            )
