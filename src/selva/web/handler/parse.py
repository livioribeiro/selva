import inspect
import typing
from collections.abc import Callable
from functools import cache
from typing import Annotated

from selva.di.inject import Inject
from selva.web.handler.model import HandlerParams, RequestParam, ServiceParam
from selva.web.routing.exception import HandlerUntypedParametersError


def assert_params_annotated(handler: Callable, *, skip: int):
    """Asserts that parameters past 'skip' are annotated.

    :raises HandlerUntypedParametersError: if parameters are not annotated.
    """
    signature = inspect.signature(handler)
    parameters = list(signature.parameters.values())

    if untyped_params := [
        p.name for p in parameters[skip:] if p.annotation is inspect.Signature.empty
    ]:
        raise HandlerUntypedParametersError(handler, untyped_params)


@cache
def parse_handler_params(handler: Callable, *, skip: int) -> HandlerParams:
    """parse handler parameters from function signature

    returns: mapping of request parameters names to 3-tuple of type,
             metadata and default value
    :raises HandlerUntypedParametersError:
    """

    assert_params_annotated(handler, skip=skip)

    result = HandlerParams([], [])

    signature = inspect.signature(handler, eval_str=True)
    parameters = list(signature.parameters.keys())

    if len(parameters) == 0:
        return result

    if inspect.ismethod(handler):  # function has `self` parameter
        skip += 1

    if len(parameters) <= skip:
        return result

    for name in parameters[skip:]:  # skip request parameter
        type_hint = signature.parameters[name].annotation
        has_default = signature.parameters[name].default is not inspect.Parameter.empty

        if typing.get_origin(type_hint) is not Annotated:
            result.request.append((name, RequestParam(type_hint, None, has_default)))
            continue

        # Annotated is garanteed to have at least 2 args
        param_type, param_meta, *_ = typing.get_args(type_hint)

        # Skip service dependencies
        if param_meta is Inject:
            result.service.append((name, ServiceParam(param_type, None, has_default)))
        elif isinstance(param_meta, Inject):
            result.service.append(
                (name, ServiceParam(param_type, param_meta.name, has_default))
            )
        else:
            result.request.append(
                (name, RequestParam(param_type, param_meta, has_default))
            )

    return result
