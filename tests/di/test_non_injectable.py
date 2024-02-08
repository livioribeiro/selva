import pytest

from selva.di.container import Container
from selva.di.error import NonInjectableTypeError


def test_non_injectable_type_should_fail(ioc: Container):
    obj = ()
    with pytest.raises(NonInjectableTypeError):
        ioc.register(obj)
