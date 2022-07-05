from selva.di import Container

from .fixtures import ioc


class Service:
    pass


async def test_define_service_not_registered(ioc: Container):
    instance = Service()
    ioc.define_singleton(Service, instance)

    service = await ioc.get(Service)

    assert service is instance


async def test_define_service_already_registered(ioc: Container):
    ioc.register(Service)
    instance = Service()
    ioc.define_singleton(Service, instance)

    service = await ioc.get(Service)

    assert service is instance
