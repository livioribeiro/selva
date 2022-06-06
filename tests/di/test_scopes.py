import pytest

from selva.di import Container, Scope
from selva.di.errors import InvalidScopeError

from .fixtures import ioc
from .utils import Context


class Service1:
    pass


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


async def test_inject_transient_into_dependent_should_fail(ioc: Container):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.DEPENDENT)
    context = Context()

    with pytest.raises(InvalidScopeError):
        await ioc.get(Service2, context=context)


async def test_inject_dependent_into_singleton_should_fail(ioc: Container):
    ioc.register(Service1, Scope.DEPENDENT)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(InvalidScopeError):
        await ioc.get(Service2)


async def test_inject_transient_into_singleton_should_fail(ioc: Container):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(InvalidScopeError):
        await ioc.get(Service2)


async def test_dependent_scope_cleanup(ioc: Container):
    ioc.register(Service1, Scope.DEPENDENT)

    context = Context()

    await ioc.get(Service1, context=context)
    assert id(context) in ioc.store_dependent

    await ioc.run_finalizers(context)

    assert len(ioc.store_dependent) == 0


async def test_context_object_is_service_itself(ioc: Container):
    ioc.register(Service1, Scope.DEPENDENT)

    instance = Service1()
    ioc.define_dependent(Service1, instance, context=instance)

    service = await ioc.get(Service1, context=instance)
    assert instance == service

    assert len(ioc.store_dependent) == 1

    await ioc.run_finalizers(instance)

    assert len(ioc.store_dependent) == 0
