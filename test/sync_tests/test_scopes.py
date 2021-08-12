import pytest

from dependency_injector.errors import InvalidScopeError

from ..utils import Context
from . import ioc


def test_inject_transient_into_dependent_should_fail(ioc):
    from .services.scopes import inject_transient_into_dependent_should_fail as module

    ioc.scan_packages(module)
    context = Context()

    with pytest.raises(InvalidScopeError):
        ioc.get(module.Service2, context=context)


def test_inject_dependent_into_singleton_should_fail(ioc):
    from .services.scopes import inject_dependent_into_singleton_should_fail as module

    ioc.scan_packages(module)
    with pytest.raises(InvalidScopeError):
        ioc.get(module.Service2)


def test_inject_transient_into_singleton_should_fail(ioc):
    from .services.scopes import inject_transient_into_singleton_should_fail as module

    ioc.scan_packages(module)
    with pytest.raises(InvalidScopeError):
        ioc.get(module.Service2)


def test_dependent_scope_cleanup(ioc):
    from .services.scopes import dependent_scope_cleanup as module

    ioc.scan_packages(module)
    context = Context()

    ioc.get(module.Service1, context=context)
    assert id(context) in ioc._container.store_dependent

    del context

    assert len(ioc._container.store_dependent) == 0
