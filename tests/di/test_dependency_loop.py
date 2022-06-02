import pytest

from selva.di import Container, Scope, initializer
from selva.di.errors import DependencyLoopError

from .fixtures import ioc


class Service1:
    def __init__(self, service2: "Service2"):
        pass


class Service2:
    def __init__(self, service1: Service1):
        pass


class LazyService:
    def __init__(self, service: "ServiceWithLazyDependency"):
        self.service = service


class ServiceWithLazyDependency:
    def __init__(self):
        self.lazy = None

    @initializer
    def initialize(self, service: LazyService):
        self.lazy = service


async def test_dependency_loop_should_fail(ioc: Container):
    ioc.register(Service1, Scope.SINGLETON)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(DependencyLoopError):
        await ioc.get(Service2)


async def test_break_dependency_loop_with_initialize_method(ioc: Container):
    ioc.register(LazyService, Scope.SINGLETON)
    ioc.register(ServiceWithLazyDependency, Scope.SINGLETON)

    result = await ioc.get(ServiceWithLazyDependency)
    assert isinstance(result.lazy, LazyService)
