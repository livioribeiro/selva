import pytest

from dependency_injector import Container
from dependency_injector.errors import DependencyLoopError

c = Container()


@c.transient
class Service1:
    def __init__(self, service2: "Service2"):
        pass


@c.transient
class Service2:
    def __init__(self, service1: Service1):
        pass


def test_dependency_loop():
    with pytest.raises(DependencyLoopError):
        c.get(Service2)
