from selva.di import Container, Scope

from .fixtures import ioc
from .utils import Context


class Service:
    pass


async def test_define_singleton_not_registered(ioc: Container):
    instance = Service()
    ioc.define_singleton(Service, instance)

    service = await ioc.get(Service)

    assert service is instance


async def test_define_singleton_already_registered(ioc: Container):
    ioc.register(Service, Scope.SINGLETON)
    instance = Service()
    ioc.define_singleton(Service, instance)

    service = await ioc.get(Service)

    assert service is instance


async def test_define_dependent_already_registered(ioc: Container):
    ioc.register(Service, Scope.DEPENDENT)
    context = Context()
    instance = Service()
    ioc.define_dependent(Service, instance, context=context)

    service = await ioc.get(Service, context=context)

    assert service is instance
