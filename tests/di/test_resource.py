from selva.di.container import Container
from selva.di.decorator import resource


class Service:
    pass


async def test_resource(ioc: Container):
    ioc.register(resource(Service))

    instance1 = await ioc.get(Service)
    instance2 = await ioc.get(Service)

    assert instance1 is not instance2
