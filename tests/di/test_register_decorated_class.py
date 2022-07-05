from selva.di import Container, service

from .fixtures import ioc


@service
class Service:
    pass


async def test_register_decorated_class(ioc: Container):
    ioc.service(Service)

    instance = await ioc.get(Service)
    assert isinstance(instance, Service)

    instance2 = await ioc.get(Service)
    assert instance is instance2
