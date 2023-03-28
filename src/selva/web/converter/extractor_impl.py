from typing import Annotated

from selva.di.decorator import service
from selva.web.context import RequestContext
from selva.web.converter.extractor import RequestParamExtractor


class FromRequestParam:
    def __init__(self, name: str | None):
        self.name = name

    def __class_getitem__(cls, item):
        match item:
            case (p_type, p_name) if (
                isinstance(p_type, type) and isinstance(p_name, str)
            ):
                return Annotated[p_type, cls(p_name)]
            case p_type if isinstance(p_type, type):
                return Annotated[p_type, cls]
            case _:
                raise TypeError()


class FromQuery(FromRequestParam):
    pass


@service(provides=RequestParamExtractor[FromQuery])
class FromQueryExtractor:
    def extract(
        self, context: RequestContext, parameter_name: str, metadata: FromQuery
    ) -> str:
        name = metadata.name or parameter_name
        return context.query.get(name)


class FromHeader(FromRequestParam):
    pass


@service(provides=RequestParamExtractor[FromHeader])
class FromHeaderExtractor:
    def extract(
        self, context: RequestContext, parameter_name: str, metadata: FromHeader
    ) -> str:
        name = metadata.name or parameter_name
        return context.headers.get(name)


class FromCookie(FromRequestParam):
    pass


@service(provides=RequestParamExtractor[FromCookie])
class FromCookieExtractor:
    def extract(
        self, context: RequestContext, parameter_name: str, metadata: FromCookie
    ) -> str:
        name = metadata.name or parameter_name
        return context.cookies.get(name)
