import inspect
from typing import Type

from asgikit.requests import Request

from selva.di.decorator import service
from selva.web.converter.param_extractor import RequestParamExtractor


class FromRequestParam:
    name: str = None

    def __init__(self, name: str = None):
        self.name = name


class FromQuery(FromRequestParam):
    pass


@service(provides=RequestParamExtractor[FromQuery])
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


@service(provides=RequestParamExtractor[FromHeader])
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


@service(provides=RequestParamExtractor[FromCookie])
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
