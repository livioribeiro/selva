import inspect
from typing import Annotated

from selva.di.decorator import ATTRIBUTE_DI_SERVICE, service
from selva.di.inject import Inject
from selva.di.service.model import ServiceInfo


def test_decorator():
    @service
    class Service:
        pass

    assert getattr(Service, ATTRIBUTE_DI_SERVICE) == ServiceInfo(None, None)


def test_class_with_dependency_annotation():
    class Dependency:
        pass

    @service
    class Service:
        dependency: Annotated[Dependency, Inject]

    init = inspect.signature(Service.__init__)
    assert len(init.parameters) == 3

    assert Service().dependency is None
    assert Service(Dependency()).dependency is not None
    assert Service(dependency=Dependency()).dependency is not None


def test_class_with_non_dependency_annotation():
    class NonDependency:
        pass

    @service
    class Service:
        non_dependency: NonDependency

    assert not hasattr(Service(), "non_dependency")
    assert not hasattr(Service(NonDependency()), "non_dependency")
    assert not hasattr(Service(non_dependency=NonDependency()), "non_dependency")


def test_class_with_mixed_dependency_annotation():
    class Dependency:
        pass

    class NonDependency:
        pass

    @service
    class Service:
        dependency: Annotated[Dependency, Inject]
        non_dependency: NonDependency

    assert Service().dependency is None
    assert Service(Dependency()).dependency is not None
    assert Service(dependency=Dependency()).dependency is not None
    assert not hasattr(Service(), "non_dependency")
    assert not hasattr(Service(NonDependency()), "non_dependency")
    assert not hasattr(Service(non_dependency=NonDependency()), "non_dependency")
