import pytest

from selva.di.container import Container
from selva.di.error import ServiceNotFoundError


class Interface:
    pass


class Impl1(Interface):
    pass


class Impl2(Interface):
    pass


def test_iter_service(ioc: Container):
    ioc.register(Impl1, provides=Interface, name="impl1")
    ioc.register(Impl2, provides=Interface, name="impl2")

    services = list(ioc.iter_service(Interface))

    assert services == [(Impl1, "impl1"), (Impl2, "impl2")]


def test_iter_service_with_not_registered_service_should_fail(ioc: Container):
    with pytest.raises(ServiceNotFoundError):
        list(ioc.iter_service(Interface))
