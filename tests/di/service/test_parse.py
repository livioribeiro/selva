from selva.di.container import Container
from selva.di.decorator import service
from selva.di.service.parse import get_dependencies


def test_register_class_with_dependency_with_non_inject_annotation(ioc: Container):
    @service
    class ServiceWithAnnotation:
        some_annotation: str

    deps = list(get_dependencies(ServiceWithAnnotation))
    assert len(deps) == 0


def test_register_factory_with_non_annotated_dependency(ioc: Container):
    class MyService:
        pass


    class Dependency:
        pass


    @service
    def factory(dep) -> MyService:
        pass

    deps = list(get_dependencies(factory))
    assert len(deps) == 1