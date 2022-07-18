from asgikit.headers import Headers
from asgikit.query import Query

from .context import RequestContext
from .from_request import FromRequest


class ContextFromRequest(FromRequest[RequestContext]):
    def from_request(self, context: RequestContext) -> RequestContext:
        return context


class HeadersFromRequest(FromRequest[Headers]):
    def from_request(self, context: RequestContext) -> Headers:
        return context.headers


class QueryFromRequest(FromRequest[Query]):
    def from_request(self, context: RequestContext) -> Headers:
        return context.query
