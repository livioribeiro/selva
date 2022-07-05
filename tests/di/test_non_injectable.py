import pytest

from selva.di import Container
from selva.di.errors import NonInjectableTypeError

from .fixtures import ioc


def test_non_injectable_type_should_fail(ioc: Container):
    obj = ()
    with pytest.raises(NonInjectableTypeError):
        ioc.register(obj)
