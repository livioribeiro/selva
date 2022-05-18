from ward import test, raises

from dependency_injector import Container, Scope
from dependency_injector.errors import InvalidScopeError

from .fixtures import ioc
from .utils import Context


class Service1:
    pass


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


@test("inject transient into dependent should fail")
async def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.DEPENDENT)
    context = Context()

    with raises(InvalidScopeError):
        await ioc.get(Service2, context=context)


@test("inject dependent into singleton should fail")
async def test_(ioc: Container = ioc):
    ioc.register(Service1, Scope.DEPENDENT)
    ioc.register(Service2, Scope.SINGLETON)

    with raises(InvalidScopeError):
        await ioc.get(Service2)


@test("inject transient into singleton should fail")
async def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.SINGLETON)

    with raises(InvalidScopeError):
        await ioc.get(Service2)


@test("dependent scope cleanup")
async def _(ioc: Container = ioc):
    ioc.register(Service1, Scope.DEPENDENT)

    context = Context()

    await ioc.get(Service1, context=context)
    assert id(context) in ioc.store_dependent

    del context

    assert len(ioc.store_dependent) == 0
