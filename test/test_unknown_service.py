import pytest

from dependency_injector.errors import UnknownServiceError

from . import ioc

pytestmark = pytest.mark.asyncio


class Service:
    pass


def test_has_unknwon_service(ioc):
    result = ioc.has(Service)
    assert not result


async def test_get_unknwon_service(ioc):
    with pytest.raises(UnknownServiceError):
        await ioc.get(Service)
