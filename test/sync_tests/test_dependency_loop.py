import pytest

from dependency_injector.errors import DependencyLoopError

from . import ioc
from .services import dependency_loop as module


def test_dependency_loop(ioc):
    ioc.scan(module)
    with pytest.raises(DependencyLoopError):
        ioc.get(module.Service2)
