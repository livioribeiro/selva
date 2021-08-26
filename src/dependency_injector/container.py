import asyncio
import inspect
import typing
import warnings
from asyncio import AbstractEventLoop
from concurrent.futures import Executor, ThreadPoolExecutor
from functools import partial
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, List, Optional, Union
from weakref import finalize

from dependency_injector.decorators import DEPENDENCY_ATRIBUTE
from dependency_injector.errors import (
    CalledNonCallableError,
    DependencyLoopError,
    FactoryMissingReturnTypeError,
    IncompatibleTypesError,
    InvalidScopeError,
    MissingDependentContextError,
    NonInjectableTypeError,
    ServiceAlreadyRegisteredError,
    UnknownServiceError,
)
from dependency_injector.scan import scan_packages
from dependency_injector.service import InjectableType, Scope, ServiceDefinition


class Container:
    def __init__(self, loop: AbstractEventLoop = None, executor: Executor = None):
        self.registry: Dict[type, ServiceDefinition] = {}
        self.store_singleton: Dict[type, Any] = {}
        self.store_dependent: Dict[int, Dict[type, Any]] = {}
        self.loop = loop or asyncio.get_event_loop()
        self.executor = executor or ThreadPoolExecutor()

    def register(self, service: InjectableType, scope: Scope, *, provides: type = None):
        if inspect.isclass(service):
            service = typing.cast(type, service)
            if provides and not issubclass(service, provides):
                raise IncompatibleTypesError(service, provides)

            provided_service = provides or service
        elif inspect.isfunction(service):
            service = typing.cast(FunctionType, service)
            if provides:
                msg = "option 'provides' on a factory function has no effect"
                warnings.warn(UserWarning(msg))

            service_type = typing.get_type_hints(service).get("return")
            if service_type is None:
                raise FactoryMissingReturnTypeError(service)
            provided_service = service_type
        else:
            raise NonInjectableTypeError(service)

        if provided_service in self.registry:
            raise ServiceAlreadyRegisteredError(provided_service)

        self.registry[provided_service] = ServiceDefinition(
            provides=provided_service, scope=scope, factory=service
        )

    def scan(self, *packages: Union[str, ModuleType]):
        for service in scan_packages(*packages):
            scope, provides = getattr(service, DEPENDENCY_ATRIBUTE)
            self.register(service, scope, provides=provides)

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

    async def create(self, service: type, *, context: Any = None) -> Any:
        dependencies = {
            n: (await self._get(s, context, Scope.TRANSIENT))
            for n, s in typing.get_type_hints(service.__init__).items()
        }
        return service(**dependencies)

    async def _create_service(
        self,
        valid_scope: Scope,
        stack: List[type],
        definition: ServiceDefinition,
        context: Any = None,
    ) -> Any:
        factory = definition.factory

        types = typing.get_type_hints(
            factory.__init__ if inspect.isclass(factory) else factory
        )
        types.pop("return", None)

        params = {
            name: await self._get(svc, context, valid_scope, stack)
            for name, svc in types.items()
        }

        if asyncio.iscoroutinefunction(factory):
            return await factory(**params)

        return await self.loop.run_in_executor(
            self.executor, partial(factory, **params)
        )

    async def call(
        self,
        callable_obj: Callable,
        *,
        context: Any = None,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> Any:
        args = args or list()
        kwargs = kwargs or dict()

        if not callable(callable_obj):
            raise CalledNonCallableError(callable_obj)

        if inspect.isfunction(callable_obj):
            func = callable_obj
        else:
            func = callable_obj.__call__

        types = [(k, v) for k, v in typing.get_type_hints(func).items() if self.has(v)]

        params = {name: await self.get(svc, context=context) for name, svc in types}

        params.update(kwargs)

        func_args = inspect.signature(func).bind(*args, **params)
        func_args.apply_defaults()

        if asyncio.iscoroutinefunction(func):
            return await func(*func_args.args, **func_args.kwargs)

        return await self.loop.run_in_executor(
            self.executor, partial(func, *func_args.args, **func_args.kwargs)
        )
