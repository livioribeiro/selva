from asgikit.requests import Request

from selva.web.converter.decorator import register_param_extractor
from selva.web.converter.error import PathParamNotFoundError
from selva.web.converter.param_extractor import (
    FromCookie,
    FromHeader,
    FromPath,
    FromQuery,
)

__all__ = (
    "FromPath",
    "FromQuery",
    "FromHeader",
    "FromCookie",
)


@register_param_extractor(FromPath)
class FromPathExtractor:
    @staticmethod
    def extract(
        request: Request,
        parameter_name: str,
        metadata: FromPath | type[FromPath],
    ) -> str:
        if isinstance(metadata, FromPath):
            name = metadata.name or parameter_name
        else:
            name = parameter_name

        param = request["path_params"].get(name)
        if not param:
            raise PathParamNotFoundError(name)

        return param


@register_param_extractor(FromQuery)
class FromQueryExtractor:
    @staticmethod
    def extract(
        request: Request,
        parameter_name: str,
        metadata: FromQuery | type[FromQuery],
    ) -> str:
        if isinstance(metadata, FromQuery):
            name = metadata.name or parameter_name
        else:
            name = parameter_name

        return request.query.get(name)


@register_param_extractor(FromHeader)
class FromHeaderExtractor:
    @staticmethod
    def extract(
        request: Request,
        parameter_name: str,
        metadata: FromHeader | type[FromHeader],
    ) -> str | None:
        if isinstance(metadata, FromHeader):
            name = metadata.name or parameter_name
        else:
            name = parameter_name

        candidate_names = (
            name,
            name.lower(),
            "-".join(name.split("_")),
            "-".join(i.capitalize() for i in name.split("_")),
        )

        for cand in candidate_names:
            if value := request.headers.get(cand):
                return value

        return None


@register_param_extractor(FromCookie)
class FromCookieExtractor:
    @staticmethod
    def extract(
        request: Request,
        parameter_name: str,
        metadata: FromCookie | type[FromCookie],
    ) -> str:
        if isinstance(metadata, FromCookie):
            name = metadata.name or parameter_name
        else:
            name = parameter_name

        return request.cookie.get(name)
