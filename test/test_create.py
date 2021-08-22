import pytest

from dependency_injector import Scope

from . import ioc
from .utils import Context

pytestmark = pytest.mark.asyncio


class Service1:
    pass


def service1_factory() -> Service1:
    return Service1()


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


def service2_factory(service1: Service1) -> Service2:
    return Service2(service1)


class Creatable:
    def __init__(self, service2: Service2):
        self.service2 = service2


async def test_create_object_register_class(ioc):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.TRANSIENT)

    result = await ioc.create(Creatable)

    assert isinstance(result.service2, Service2)
    assert isinstance(result.service2.service1, Service1)


async def test_create_object_register_factory(ioc):
    ioc.register(service1_factory, Scope.TRANSIENT)
    ioc.register(service2_factory, Scope.TRANSIENT)

    result = await ioc.create(Creatable)

    assert isinstance(result.service2, Service2)
    assert isinstance(result.service2.service1, Service1)


async def test_create_object_with_context(ioc):
    ioc.register(Service1, Scope.DEPENDENT)
    ioc.register(Service2, Scope.DEPENDENT)

    context = Context()

    result1 = await ioc.create(Creatable, context=context)

    assert isinstance(result1.service2, Service2)
    assert isinstance(result1.service2.service1, Service1)

    result2 = await ioc.create(Creatable, context=context)

    assert result2 is not result1
    assert result2.service2 is result1.service2
