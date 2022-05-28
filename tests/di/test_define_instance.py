from selva.di import Container

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
    ioc.register_singleton(Service)
    instance = Service()
    ioc.define_singleton(Service, instance)

    service = await ioc.get(Service)

    assert service is instance


async def test_define_dependent_already_registered(ioc: Container):
    ioc.register_dependent(Service)
    context = Context()
    instance = Service()
    ioc.define_dependent(Service, instance, context=context)

    service = await ioc.get(Service, context=context)

    assert service is instance
