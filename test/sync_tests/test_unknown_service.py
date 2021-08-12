import pytest

from dependency_injector.errors import UnknownServiceError

from . import ioc


class Service:
    pass


def test_has_unknwon_service(ioc):
    result = ioc.has(Service)
    assert not result


def test_get_unknwon_service(ioc):
    with pytest.raises(UnknownServiceError):
        ioc.get(Service)
