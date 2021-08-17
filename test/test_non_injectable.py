from types import SimpleNamespace

import pytest

from dependency_injector import Scope
from dependency_injector.errors import NonInjectableTypeError

from . import ioc


def test_non_injectable(ioc):
    obj = SimpleNamespace()
    with pytest.raises(NonInjectableTypeError):
        ioc.register(obj, Scope.SINGLETON)
