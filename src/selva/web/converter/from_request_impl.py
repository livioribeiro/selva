import inspect
from abc import ABC
from http import HTTPMethod
from typing import Annotated, Any, TypeVar, get_args, get_origin

from asgikit.requests import Body, Request

from selva._util.base_types import get_base_types
from selva._util.maybe_async import maybe_async
from selva.di.container import Container
from selva.di.error import ServiceNotFoundError
from selva.di.inject import Inject
from selva.web.converter.converter import Converter
from selva.web.converter.decorator import register_from_request
from selva.web.converter.error import (
    FromBodyOnWrongHttpMethodError,
    MissingConverterImplError,
    MissingRequestParamExtractorImplError,
)
from selva.web.converter.param_extractor import (
    FromBody,
    FromCookie,
    FromHeader,
    FromPath,
    FromQuery,
    ParamExtractor,
)
from selva.web.exception import HTTPBadRequestException


@register_from_request(FromBody)
class BodyFromRequest(FromBody):
    di: Annotated[Container, Inject]

    async def from_request(
        self,
        request: Request,
        original_type: type,
        parameter_name: str,
        _metadata,
        _optional: bool,
    ) -> Any:
        if request.method not in (HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH):
            raise FromBodyOnWrongHttpMethodError(parameter_name)

        if (origin := get_origin(original_type)) is list:
            search_type = get_args(original_type)[0]
            search_types = [
                origin[base_type] for base_type in get_base_types(search_type)
            ]
        elif original_type is dict:
            search_types = [dict]
        else:
            search_types = get_base_types(original_type)

        for base_type in search_types:
            if converter := await self.di.get(
                Converter[Body, base_type], optional=True
            ):
                return await maybe_async(converter.convert(request.body, original_type))

        raise MissingConverterImplError(original_type)


T_EXTRACTOR = TypeVar("T_EXTRACTOR")


class RequestParamFromRequest(ABC):
    di: Annotated[Container, Inject]
    extractor_type: type[T_EXTRACTOR]

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    async def from_request(
        self,
        request: Request,
        original_type: type,
        parameter_name: str,
        metadata: T_EXTRACTOR | type[T_EXTRACTOR],
        optional: bool,
    ):
        parameter_type = metadata if inspect.isclass(metadata) else type(metadata)
        try:
            extractor = await self.di.get(ParamExtractor[parameter_type])
        except ServiceNotFoundError:
            # pylint: disable=raise-missing-from
            raise MissingRequestParamExtractorImplError(parameter_type)

        converter = await self.di.get(Converter[str, original_type])

        if data := extractor.extract(request, parameter_name, metadata):
            return converter.convert(data, original_type)

        if optional:
            return None

        raise HTTPBadRequestException()


@register_from_request(FromPath)
class PathParamFromRequest(RequestParamFromRequest):
    extractor_type = FromPath


@register_from_request(FromQuery)
class QueryParamFromRequest(RequestParamFromRequest):
    extractor_type = FromQuery


@register_from_request(FromHeader)
class HeaderParamFromRequest(RequestParamFromRequest):
    extractor_type = FromHeader


@register_from_request(FromCookie)
class CookieParamFromRequest(RequestParamFromRequest):
    extractor_type = FromCookie
