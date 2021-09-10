import pytest

from dependency_injector import Scope
from dependency_injector.errors import InvalidScopeError

from ..utils import Context
from . import ioc


class Service1:
    pass


class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


def test_inject_transient_into_dependent_should_fail(ioc):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.DEPENDENT)
    context = Context()

    with pytest.raises(InvalidScopeError):
        ioc.get(Service2, context=context)


def test_inject_dependent_into_singleton_should_fail(ioc):
    ioc.register(Service1, Scope.DEPENDENT)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(InvalidScopeError):
        ioc.get(Service2)


def test_inject_transient_into_singleton_should_fail(ioc):
    ioc.register(Service1, Scope.TRANSIENT)
    ioc.register(Service2, Scope.SINGLETON)

    with pytest.raises(InvalidScopeError):
        ioc.get(Service2)


def test_dependent_scope_cleanup(ioc):
    ioc.register(Service1, Scope.DEPENDENT)

    context = Context()

    ioc.get(Service1, context=context)
    assert id(context) in ioc.store_dependent

    del context

    assert len(ioc.store_dependent) == 0
