import inspect
from typing import Annotated

from selva.di.decorator import DI_ATTRIBUTE_SERVICE, service
from selva.di.inject import Inject
from selva.di.service.model import ServiceInfo


def test_decorator():
    @service
    def factory():
        pass

    assert getattr(factory, DI_ATTRIBUTE_SERVICE) == ServiceInfo(None)
