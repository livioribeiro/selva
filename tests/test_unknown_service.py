from ward import test, raises

from dependency_injector import Container, Scope
from dependency_injector.errors import ServiceNotFoundError

from .fixtures import ioc


class Service:
    pass


@test("has unknwon service")
def _(ioc: Container = ioc):
    result = ioc.has(Service)
    assert not result


@test("get unknwon service")
async def _(ioc: Container = ioc):
    with raises(ServiceNotFoundError):
        await ioc.get(Service)


@test("service with name not found")
async def _(ioc: Container = ioc):
    ioc.register(Service, Scope.TRANSIENT, name="1")
    with raises(ServiceNotFoundError):
        await ioc.get(Service, name="2")
