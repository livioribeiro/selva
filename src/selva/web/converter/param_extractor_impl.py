import inspect
from typing import Type

from asgikit.requests import Request

from selva.web.converter.decorator import register_param_extractor
from selva.web.converter.error import PathParamNotFoundError

__all__ = (
    "FromPath",
    "FromQuery",
    "FromHeader",
    "FromCookie",
)


class FromRequestParam:
    name: str = None

    def __init__(self, name: str = None):
        self.name = name


class FromPath(FromRequestParam):
    pass


@register_param_extractor(FromPath)
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


@register_param_extractor(FromQuery)
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


@register_param_extractor(FromHeader)
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


@register_param_extractor(FromCookie)
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
