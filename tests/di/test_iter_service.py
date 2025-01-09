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


class AnotherInterface:
    pass


@service(provides=AnotherInterface)
class AnotherImpl(AnotherInterface):
    pass


def test_iter_service(ioc: Container):
    ioc.register(Impl1)
    ioc.register(Impl2)

    result = list(ioc.iter_service(Interface))

    assert result == [(Impl1, "impl1"), (Impl2, "impl2")]


def test_iter_all_services(ioc: Container):
    ioc.register(Impl1)
    ioc.register(Impl2)
    ioc.register(AnotherImpl)

    result = list(ioc.iter_all_services())
    assert result == [
        (Interface, Impl1, "impl1"),
        (Interface, Impl2, "impl2"),
        (AnotherInterface, AnotherImpl, None),
    ]


def test_iter_service_with_not_registered_service_should_fail(ioc: Container):
    with pytest.raises(ServiceNotFoundError):
        list(ioc.iter_service(Interface))
