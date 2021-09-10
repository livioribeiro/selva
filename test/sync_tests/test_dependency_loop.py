from __future__ import annotations

import pytest

from dependency_injector import Scope
from dependency_injector.errors import DependencyLoopError
from dependency_injector.lazy import Lazy

from . import ioc


class Service1:
    def __init__(self, service2: Service2):
        pass


class Service2:
    def __init__(self, service1: Service1):
        pass


class LazyService:
    def __init__(self, service: ServiceWithLazyDependency):
        self.service = service


class ServiceWithLazyDependency:
    def __init__(self, service: Lazy[LazyService]):
        self.service = service


def test_dependency_loop(ioc):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(DependencyLoopError):
        ioc.get(Service2)


def test_break_dependency_loop_with_lazy(ioc):
    ioc.register(LazyService, Scope.SINGLETON)
    ioc.register(ServiceWithLazyDependency, Scope.SINGLETON)

    result = ioc.get(LazyService)
    dependent = result.service.service.get()
    assert isinstance(result.service, ServiceWithLazyDependency)
    assert isinstance(dependent, LazyService)
