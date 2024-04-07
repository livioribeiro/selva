import pytest

from selva.di.container import Container
from selva.di.decorator import service
from selva.di.error import ServiceNotFoundError


class Interface:
    pass


@service(provides=Interface, name="impl1")
class Impl1(Interface):
    pass


@service(provides=Interface, name="impl2")
class Impl2(Interface):
    pass


def test_iter_service(ioc: Container):
    ioc.register(Impl1)
    ioc.register(Impl2)

    services = list(ioc.iter_service(Interface))

    assert services == [(Impl1, "impl1"), (Impl2, "impl2")]


def test_iter_service_with_not_registered_service_should_fail(ioc: Container):
    with pytest.raises(ServiceNotFoundError):
        list(ioc.iter_service(Interface))
