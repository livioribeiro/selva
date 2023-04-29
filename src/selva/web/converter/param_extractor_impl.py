from selva.di.decorator import service
from selva.web.context import RequestContext
from selva.web.converter.param_extractor import RequestParamExtractor


class FromRequestParam:
    def __init__(self, name: str = None):
        self.name = name


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
    ) -> str | None:
        name = metadata.name or parameter_name
        candidate_names = (
            name,
            name.lower(),
            "-".join(name.split("_")),
            "-".join(i.capitalize() for i in name.split("_")),
        )

        for cand in candidate_names:
            if value := context.headers.get(cand):
                return value

        return None


class FromCookie(FromRequestParam):
    pass


@service(provides=RequestParamExtractor[FromCookie])
class FromCookieExtractor:
    def extract(
        self, context: RequestContext, parameter_name: str, metadata: FromCookie
    ) -> str:
        name = metadata.name or parameter_name
        return context.cookies.get(name)
