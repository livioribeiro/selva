import pytest

from selva.di import Container, Scope
from selva.di.errors import ServiceNotFoundError

from .fixtures import ioc


class Service:
    pass


def test_has_unknwon_service(ioc: Container):
    result = ioc.has(Service)
    assert not result


async def test_get_unknwon_service(ioc: Container):
    with pytest.raises(ServiceNotFoundError):
        await ioc.get(Service)


async def test_service_with_name_not_found(ioc: Container):
    ioc.register(Service, Scope.TRANSIENT, name="1")
    with pytest.raises(ServiceNotFoundError):
        await ioc.get(Service, name="2")
