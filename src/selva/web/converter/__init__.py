from abc import ABC
from collections.abc import Mapping

from selva.web.converter.decorator import (
    register_converter,
    register_from_request,
    register_param_extractor,
)

__all__ = (
    "register_converter",
    "register_from_request",
    "register_param_extractor",
    "Json",
    "Form",
)


class Json(ABC):
    pass


class Form(Mapping, ABC):
    pass
