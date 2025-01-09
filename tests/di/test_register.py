import pytest

from selva.di.container import Container
from selva.di.error import ServiceWithoutDecoratorError


class ServiceClass:
    pass


def service_factory() -> ServiceClass:
    return ServiceClass()


@pytest.mark.parametrize(
    "injectable", [ServiceClass, service_factory], ids=["class", "function"]
)
def test_register_service_without_decorator_should_fail(injectable, ioc: Container):
    with pytest.raises(ServiceWithoutDecoratorError):
        ioc.register(ServiceClass)
