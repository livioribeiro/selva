import pytest

from dependency_injector import Container

from .context import Context


def test_inject_singleton():
    c = Container()

    @c.singleton
    class Service1:
        pass

    @c.singleton
    class Service2:
        def __init__(self, service1: Service1):
            self.service1 = service1

    service = c.get(Service2)
    assert isinstance(service, Service2)
    assert type(service.service1) == Service1

    other_service = c.get(Service2)
    assert id(other_service) == id(service)
    assert id(other_service.service1) == id(service.service1)


def test_inject_transient():
    c = Container()

    @c.transient
    class Service1:
        pass

    @c.transient
    class Service2:
        def __init__(self, service1: Service1):
            self.service1 = service1

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
    class Service1:
        pass

    @c.dependent
    class Service2:
        def __init__(self, service1: Service1):
            self.service1 = service1

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


def test_dependent_without_context():
    c = Container()

    @c.dependent
    class Service1:
        pass

    with pytest.raises(ValueError):
        c.get(Service1)
