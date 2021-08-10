from abc import ABC, abstractmethod

import pytest

from dependency_injector import Container, Scope
from dependency_injector.errors import IncompatibleTypesError


def test_has_class_service():
    c = Container()

    @c.transient
    class Service1:
        pass

    result = c.has(Service1)
    assert result


def test_has_function_service():
    c = Container()

    class Service1:
        pass

    @c.transient
    def service1_factory() -> Service1:
        return Service1()

    result = c.has(Service1)
    assert result


def test_has_service_with_scope():
    c = Container()

    @c.transient
    class ServiceTransient:
        pass

    @c.dependent
    class ServiceDependent:
        pass

    @c.singleton
    class ServiceSingleton:
        pass

    result_transient = c.has(ServiceTransient, Scope.TRANSIENT)
    result_dependent = c.has(ServiceDependent, Scope.DEPENDENT)
    result_singleton = c.has(ServiceSingleton, Scope.SINGLETON)

    assert result_transient
    assert result_dependent
    assert result_singleton


def test_has_unknwon_service():
    c = Container()

    class Service1:
        pass

    result = c.has(Service1)
    assert not result


def test_get_unknwon_service():
    c = Container()

    class Service1:
        pass

    with pytest.raises(ValueError):
        c.get(Service1)


def test_provides_class():
    c = Container()

    class Interface(ABC):
        @abstractmethod
        def method(self):
            pass

    @c.singleton(provides=Interface)
    class Implementation(Interface):
        def method(self):
            pass

    service = c.get(Interface)
    assert isinstance(service, Implementation)


def test_provides_function():
    c = Container()

    class Interface(ABC):
        @abstractmethod
        def method(self):
            pass

    class Implementation(Interface):
        def method(self):
            pass

    @c.singleton
    def factory() -> Interface:
        return Implementation()

    service = c.get(Interface)
    assert isinstance(service, Implementation)


def test_incompatible_types():
    c = Container()

    class Interface(ABC):
        @abstractmethod
        def method(self):
            pass

    with pytest.raises(IncompatibleTypesError):

        @c.singleton(provides=Interface)
        class Implementation:
            def method(self):
                pass
