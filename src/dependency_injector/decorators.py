import inspect
import warnings
from types import FunctionType
from typing import Union, get_type_hints

from .errors import (
    FactoryMissingReturnTypeError,
    IncompatibleTypesError,
    NonInjectableTypeError,
)
from .service import Scope, ServiceDefinition

InjectableType = Union[type, FunctionType]


def singleton(service: InjectableType = None, *, provides: type = None):
    return register(service, scope=Scope.SINGLETON, provides=provides)


def dependent(service: InjectableType = None, *, provides: type = None):
    return register(service, scope=Scope.DEPENDENT, provides=provides)


def transient(service: InjectableType = None, *, provides: type = None):
    return register(service, scope=Scope.TRANSIENT, provides=provides)


def register(service: InjectableType = None, *, scope: Scope, provides: type = None):
    def register_func(service: InjectableType):
        if inspect.isclass(service):
            if provides and not issubclass(service, provides):
                raise IncompatibleTypesError(service, provides)

            provided_service = provides or service
        elif inspect.isfunction(service):
            if provides:
                warnings.warn(
                    UserWarning("option 'provides' on a factory function has no effect")
                )

            service_type = get_type_hints(service).get("return")
            if service_type is None:
                raise FactoryMissingReturnTypeError(service)
            provided_service = service_type
        else:
            raise NonInjectableTypeError(service)

        service_info = ServiceDefinition(
            provides=provided_service, scope=scope, factory=service
        )
        setattr(service, "__dependency_injector__", service_info)
        return service

    return register_func(service) if service else register_func
