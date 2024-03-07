from typing import Any

from selva.di.decorator import DI_ATTRIBUTE_SERVICE


def is_resource(candidate: Any) -> bool:
    if info := getattr(candidate, DI_ATTRIBUTE_SERVICE, None):
        return info.resource
    return False
