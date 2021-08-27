import pytest

from dependency_injector import Scope
from dependency_injector.errors import InvalidScopeError

from . import ioc
from .utils import Context

pytestmark = pytest.mark.asyncio


class Service1:
    pass


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


async def test_inject_transient_into_dependent_should_fail(ioc):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.DEPENDENT)
    context = Context()

    with pytest.raises(InvalidScopeError):
        await ioc.get(Service2, context=context)


async def test_inject_dependent_into_singleton_should_fail(ioc):
    ioc.register(Service1, Scope.DEPENDENT)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(InvalidScopeError):
        await ioc.get(Service2)


async def test_inject_transient_into_singleton_should_fail(ioc):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(InvalidScopeError):
        await ioc.get(Service2)


async def test_dependent_scope_cleanup(ioc):
    ioc.register(Service1, Scope.DEPENDENT)

    context = Context()

    await ioc.get(Service1, context=context)
    assert id(context) in ioc.store_dependent

    del context

    assert len(ioc.store_dependent) == 0
