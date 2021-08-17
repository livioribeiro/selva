import pytest

from dependency_injector.errors import InvalidScopeError

from . import ioc
from .utils import Context

pytestmark = pytest.mark.asyncio


async def test_inject_transient_into_dependent_should_fail(ioc):
    from .services.scopes import inject_transient_into_dependent_should_fail as module

    ioc.scan(module)
    context = Context()

    with pytest.raises(InvalidScopeError):
        await ioc.get(module.Service2, context=context)


async def test_inject_dependent_into_singleton_should_fail(ioc):
    from .services.scopes import inject_dependent_into_singleton_should_fail as module

    ioc.scan(module)
    with pytest.raises(InvalidScopeError):
        await ioc.get(module.Service2)


async def test_inject_transient_into_singleton_should_fail(ioc):
    from .services.scopes import inject_transient_into_singleton_should_fail as module

    ioc.scan(module)
    with pytest.raises(InvalidScopeError):
        await ioc.get(module.Service2)


async def test_dependent_scope_cleanup(ioc):
    from .services.scopes import dependent_scope_cleanup as module

    ioc.scan(module)
    context = Context()

    await ioc.get(module.Service1, context=context)
    assert id(context) in ioc.store_dependent

    del context

    assert len(ioc.store_dependent) == 0
