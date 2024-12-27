import inspect
from typing import Type

from asgikit.requests import Request

from selva.di.decorator import service
from selva.web.converter.error import PathParamNotFoundError

__all__ = (
    "FromPath",
    "FromQuery",
    "FromHeader",
    "FromCookie",
)

from selva.web.converter.param_extractor import ParamExtractor


class FromRequestParam:
    name: str = None

    def __init__(self, name: str = None):
        self.name = name


class FromPath(FromRequestParam):
    pass


@service
async def from_path_extractor(_) -> ParamExtractor["FromPath"]:
    return FromPathExtractor()


@service
async def from_query_extractor(_) -> ParamExtractor["FromQuery"]:
    return FromQueryExtractor()


@service
async def from_header_extractor(_) -> ParamExtractor["FromHeader"]:
    return FromHeaderExtractor()


@service
async def from_cookie_extractor(_) -> ParamExtractor["FromCookie"]:
    return FromCookieExtractor()


class FromPathExtractor:
    @staticmethod
    def extract(
        request: Request,
        parameter_name: str,
        metadata: FromPath | Type[FromPath],
    ) -> str:
        if inspect.isclass(metadata):
            name = parameter_name
        else:
            name = metadata.name or parameter_name

        param = request["path_params"].get(name)
        if not param:
            raise PathParamNotFoundError(name)

        return param


class FromQuery(FromRequestParam):
    pass


class FromQueryExtractor:
    @staticmethod
    def extract(
        request: Request,
        parameter_name: str,
        metadata: FromQuery | Type[FromQuery],
    ) -> str:
        if inspect.isclass(metadata):
            name = parameter_name
        else:
            name = metadata.name or parameter_name

        return request.query.get(name)


class FromHeader(FromRequestParam):
    pass


class FromHeaderExtractor:
    @staticmethod
    def extract(
        request: Request,
        parameter_name: str,
        metadata: FromHeader | Type[FromHeader],
    ) -> str | None:
        if inspect.isclass(metadata):
            name = parameter_name
        else:
            name = metadata.name or parameter_name

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


class FromCookie(FromRequestParam):
    pass


class FromCookieExtractor:
    @staticmethod
    def extract(
        request: Request,
        parameter_name: str,
        metadata: FromCookie | Type[FromCookie],
    ) -> str:
        if inspect.isclass(metadata):
            name = parameter_name
        else:
            name = metadata.name or parameter_name

        return request.cookie.get(name)
