import inspect
from abc import ABC
from http import HTTPMethod
from typing import Annotated, Any, Union, get_origin, get_args

from asgikit.requests import Request

from selva._util.maybe_async import maybe_async
from selva._util.base_types import get_base_types
from selva.di.container import Container
from selva.di.inject import Inject
from selva.web.converter.converter import Converter
from selva.web.converter.decorator import register_from_request
from selva.web.converter.param_extractor import ParamExtractor, FromBody, FromPath, FromQuery, FromHeader, FromCookie


@register_from_request(FromBody)
class BodyFromRequest(FromBody):
    di: Annotated[Container, Inject]

    async def from_request(
            self,
            request: Request,
            original_type: type,
            parameter_name: str,
            metadata=None,
    ) -> Any:
        if request.method not in (HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH):
            raise TypeError(
                "`FromBody` parameter on method that does not accept body"
            )

        if (origin := get_origin(original_type)) is list:
            search_type = get_args(original_type)[0]
            search_types = [origin[base_type] for base_type in get_base_types(search_type)]
        elif original_type is dict:
            search_types = [dict]
        else:
            search_types = get_base_types(original_type)

        for base_type in search_types:
            if converter := await self.di.get(Converter[Request, base_type], optional=True):
                return await maybe_async(converter.convert(request, original_type))

        raise TypeError(f"No converter available for {original_type}")


class RequestParamFromRequest(ABC):
    di: Annotated[Container, Inject]
    extractor_type: type

    async def from_request(
        self,
        request: Request,
        original_type: type,
        parameter_name: str,
        metadata: Union["extractor_type", type["extractor_type"]],
    ):
        parameter_type = metadata if inspect.isclass(metadata) else type(metadata)
        extractor = await self.di.get(ParamExtractor[parameter_type], optional=True)
        converter = await self.di.get(Converter[str, original_type], optional=True)

        if data := extractor.extract(request, parameter_name, metadata):
            return converter.convert(data, original_type)
        return None


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
