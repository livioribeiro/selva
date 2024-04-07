from selva.di.container import Container


class Service:
    pass


async def test_define_service_not_registered(ioc: Container):
    instance = Service()
    ioc.define(Service, instance)

    service = await ioc.get(Service)

    assert service is instance


async def test_define_service_already_registered(ioc: Container):
    instance = Service()
    ioc.define(Service, instance)

    service = await ioc.get(Service)

    assert service is instance
