import pytest

from dependency_injector.errors import NonInjectableTypeError

from . import ioc


def test_non_injectable():
    with pytest.raises(NonInjectableTypeError):
        from .services import non_injectable
