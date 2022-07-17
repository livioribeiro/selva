from functools import cache
from typing import Generic, Protocol, get_origin

__all__ = ("get_base_types",)


@cache
def get_base_types(base_class: type) -> list[type | Generic]:
    if origin := get_origin(base_class):
        result = [base_class] + list(origin.mro())
        base_class = origin
    else:
        result = list(base_class.mro())

    # remove 'object' type
    result.pop()

    if Generic in result:
        if Protocol in result:
            index = result.index(Protocol)
        else:
            index = result.index(Generic)

        result = result[:index]

    for origin, generic in _get_generic_origins(base_class):
        if origin in result:
            index = result.index(origin)
            result.insert(index, generic)

    return result


def _get_generic_origins(base_class):
    if orig_bases := getattr(base_class, "__orig_bases__", None):
        for generic in orig_bases:
            origin = get_origin(generic)
            yield origin, generic
            yield from _get_generic_origins(origin)
