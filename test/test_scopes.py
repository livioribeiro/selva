import pytest

from dependency_injector import Container
from dependency_injector.errors import InvalidScopeError

from .context import Context


def test_inject_transient_into_dependent():
    c = Container()
    context = Context()

    @c.transient
    class Service1:
        pass

    @c.dependent
    class Service2:
        def __init__(self, service1: Service1):
            self.service1 = service1

    with pytest.raises(InvalidScopeError):
        c.get(Service2, context=context)


def test_inject_dependent_into_singleton():
    c = Container()

    @c.dependent
    class Service1:
        pass

    @c.singleton
    class Service2:
        def __init__(self, service1: Service1):
            self.service1 = service1

    with pytest.raises(InvalidScopeError):
        c.get(Service2)


def test_inject_transient_into_singleton():
    c = Container()

    @c.transient
    class Service1:
        pass

    @c.singleton
    class Service2:
        def __init__(self, service1: Service1):
            self.service1 = service1

    with pytest.raises(InvalidScopeError):
        c.get(Service2)


def test_dependent_scope():
    c = Container()
    context = Context()

    @c.dependent
    class Service1:
        pass

    c.get(Service1, context=context)
    assert id(context) in c.store_dependent

    context = None

    assert len(c.store_dependent) == 0
