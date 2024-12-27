import inspect
import typing
from collections.abc import Callable

import structlog
from mypy.fastparse import FunctionType

from selva.di.error import (
    FactoryMissingReturnTypeError,
    NonInjectableTypeError,
)
from selva.di.service.model import InjectableType, ServiceSpec

logger = structlog.get_logger()


def parse_service_spec(
    service: FunctionType,
    name: str = None,
) -> ServiceSpec:
    if not inspect.isfunction(service):
        raise NonInjectableTypeError(service)

    type_hints = typing.get_type_hints(service)
    return_type = type_hints.pop("return")

    if return_type is None:
        raise FactoryMissingReturnTypeError(service)

    receives_locator = len(inspect.signature(service).parameters) > 0

    return ServiceSpec(
        provides=return_type,
        factory=service,
        name=name,
        receives_locator=receives_locator,
    )
