import pytest

from dependency_injector import Scope
from dependency_injector.errors import ServiceNotFoundError

from . import ioc

pytestmark = pytest.mark.asyncio


class Service:
    pass


def test_has_unknwon_service(ioc):
    result = ioc.has(Service)
    assert not result


async def test_get_unknwon_service(ioc):
    with pytest.raises(ServiceNotFoundError):
        await ioc.get(Service)


async def test_service_with_name_not_found(ioc):
    ioc.register(Service, Scope.TRANSIENT, name="1")
    with pytest.raises(ServiceNotFoundError):
        await ioc.get(Service, name="2")
