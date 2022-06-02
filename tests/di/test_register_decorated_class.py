from selva.di import Container, Scope, service

from .fixtures import ioc
from .utils import Context


@service
class Service:
    pass


@service(scope=Scope.DEPENDENT)
class Dependent:
    pass


@service(scope=Scope.TRANSIENT)
class Transient:
    pass


async def test_register_decorated_class(ioc: Container):
    ioc.service(Service)

    instance = await ioc.get(Service)
    assert isinstance(instance, Service)

    instance2 = await ioc.get(Service)
    assert instance is instance2


async def test_register_decorated_class_dependent(ioc: Container):
    ioc.service(Dependent)

    context = Context()
    instance = await ioc.get(Dependent, context=context)
    instance2 = await ioc.get(Dependent, context=context)
    assert instance is instance2

    context2 = Context()
    instance3 = await ioc.get(Dependent, context=context2)
    assert instance is not instance3


async def test_register_decorated_class_transient(ioc: Container):
    ioc.service(Transient)

    instance = await ioc.get(Transient)
    instance2 = await ioc.get(Transient)

    assert instance is not instance2
