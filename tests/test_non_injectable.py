from types import SimpleNamespace

from ward import test, raises

from dependency_injector import Scope
from dependency_injector.errors import NonInjectableTypeError

from .fixtures import ioc


@test("non injectable type should fail")
def test_non_injectable(ioc=ioc):
    obj = SimpleNamespace()
    with raises(NonInjectableTypeError):
        ioc.register(obj, Scope.SINGLETON)
