import functools
import inspect
from collections.abc import Callable
from typing import Any

from asgikit.requests import Request

from selva._util.maybe_async import maybe_async
from selva.di.container import Container
from selva.web.converter.error import MissingFromRequestImplError
from selva.web.converter.from_request import FromRequest
from selva.web.handler.parse import parse_handler_params


async def call_handler(
    di: Container, handler: Callable, request: Request, *, skip: int
):
    actual_handler = handler
    while isinstance(actual_handler, functools.partial):
        actual_handler = actual_handler.func

    handler_params = parse_handler_params(actual_handler, skip=skip)
    request_params = await params_from_request(di, request, handler_params.request)

    request_services = {
        name: await di.get(service_type, name=service_name, optional=has_default)
        for name, (
            service_type,
            service_name,
            has_default,
        ) in handler_params.service
    }

    await handler(request, **(request_params | request_services))


async def params_from_request(
    di: Container,
    request: Request,
    params: list[tuple[str, Any, bool]],
) -> dict[str, Any]:
    result = {}

    for name, (param_type, param_annotation, has_default) in params:
        if param_annotation:
            if inspect.isclass(param_annotation):
                converter_type = param_annotation
            else:
                converter_type = type(param_annotation)
        else:
            converter_type = param_type

        if from_request_service := await di.get(FromRequest[converter_type]):
            value = await maybe_async(
                from_request_service.from_request,
                request,
                param_type,
                name,
                param_annotation,
                has_default,
            )

            if value:
                result[name] = value
        else:
            raise MissingFromRequestImplError(param_type)

    return result
