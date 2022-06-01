from selva.di import Container, singleton

from .fixtures import ioc


@singleton
class Service:
    pass


async def test_register_decorated_class(ioc: Container):
    ioc.register_service(Service)

    instance = await ioc.get(Service)
    assert isinstance(instance, Service)

    instance2 = await ioc.get(Service)
    assert instance is instance2
