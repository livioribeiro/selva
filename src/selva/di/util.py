import inspect
from collections.abc import Callable
from functools import cache
from typing import get_type_hints, get_origin, get_args, Annotated

from selva.di.inject import Inject


@cache
def parse_function_services(function: Callable, *, skip: int, require_annotation: bool) -> dict[str, tuple[type, str | None]]:
    result = {}

    parameters = list(inspect.signature(function).parameters.keys())

    if len(parameters) == 0:
        return result

    if inspect.ismethod(function): # function has `self` parameter
        skip += 1

    if len(parameters) <= skip:
        return result

    skip_params = parameters[:skip]
    type_hints = get_type_hints(function, include_extras=True)
    for param in skip_params:
        type_hints.pop(param, None)

    for name, hint in type_hints.items():
        if get_origin(hint) is Annotated:
            param_type, param_meta, *_ = get_args(hint)

            if param_meta is Inject:
                result[name] = (param_type, None)
            if isinstance(param_type, Inject):
                result[name] = (param_type, param_meta.name)
            else:
                continue

        elif not require_annotation:
            result[name] = (hint, None)

    return result
