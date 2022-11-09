from asgikit.headers import Headers
from asgikit.query import Query

from selva.di.decorators import service
from selva.web.request.context import RequestContext
from selva.web.request.from_request import FromRequest


@service(provides=FromRequest[RequestContext])
class ContextFromRequest:
    def from_request(self, context: RequestContext) -> RequestContext:
        return context


@service(provides=FromRequest[Headers])
class HeadersFromRequest:
    def from_request(self, context: RequestContext) -> Headers:
        return context.headers


@service(provides=FromRequest[Query])
class QueryFromRequest:
    def from_request(self, context: RequestContext) -> Headers:
        return context.query
