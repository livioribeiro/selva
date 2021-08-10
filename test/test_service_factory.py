import pytest

from dependency_injector import Container

from .context import Context


class Service1:
    pass


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


def test_inject_singleton():
    c = Container()

    @c.singleton
    def service1_factory() -> Service1:
        return Service1()

    @c.singleton
    def service2_factory(service1: Service1) -> Service2:
        return Service2(service1)

    service = c.get(Service2)
    assert isinstance(service, Service2)
    assert type(service.service1) == Service1

    other_service = c.get(Service2)
    assert id(other_service) == id(service)
    assert id(other_service.service1) == id(service.service1)


def test_inject_transient():
    c = Container()

    @c.transient
    def service1_factory() -> Service1:
        return Service1()

    @c.transient
    def service2_factory(service1: Service1) -> Service2:
        return Service2(service1)

    service = c.get(Service2)
    assert isinstance(service, Service2)
    assert type(service.service1) == Service1

    other_service = c.get(Service2)
    assert id(other_service) != id(service)
    assert id(other_service.service1) != id(service.service1)


def test_inject_dependent():
    c = Container()
    context = Context()

    @c.dependent
    def service1_factory() -> Service1:
        return Service1()

    @c.dependent
    def service2_factory(service1: Service1) -> Service2:
        return Service2(service1)

    service = c.get(Service2, context=context)
    assert isinstance(service, Service2)
    assert type(service.service1) == Service1

    other_service = c.get(Service2, context=context)
    assert id(other_service) == id(service)
    assert id(other_service.service1) == id(service.service1)

    context2 = Context()
    another_service = c.get(Service2, context=context2)
    assert id(another_service) != id(service)
    assert id(another_service.service1) != id(service.service1)


def test_factory_function_without_return_type():
    c = Container()

    with pytest.raises(ValueError):

        @c.dependent
        def service1_factory():
            return Service1()


def test_dependent_without_context():
    c = Container()

    @c.dependent
    def service1_factory() -> Service1:
        return Service1()

    with pytest.raises(ValueError):
        c.get(Service1)


def test_provides_option_on_function_generates_warning():
    c = Container()

    class Interface:
        def method(self):
            pass

    class Implementation(Interface):
        def method(self):
            pass

    with pytest.warns(UserWarning):

        @c.singleton(provides=Interface)
        def factory() -> Interface:
            return Implementation()
