import pytest

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import ServiceNotFoundError


@service(name="1")
class Service:
    pass


def test_has_unknwon_service(ioc: Container):
    result = ioc.has(Service)
    assert not result


async def test_get_unknwon_service(ioc: Container):
    with pytest.raises(ServiceNotFoundError):
        await ioc.get(Service)


async def test_service_with_name_not_found(ioc: Container):
    ioc.register(Service)
    with pytest.raises(ServiceNotFoundError):
        await ioc.get(Service, name="2")
