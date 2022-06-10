from asgikit.headers import Headers
from asgikit.query import Query

from selva.di import service

from .context import RequestContext
from .from_request import FromRequest


@service(provides=FromRequest[RequestContext])
class ContextFromRequest(FromRequest[RequestContext]):
    async def from_request(self, context: RequestContext) -> RequestContext:
        return context


@service(provides=FromRequest[Headers])
class HeadersFromRequest(FromRequest[Headers]):
    async def from_request(self, context: RequestContext) -> Headers:
        return context.headers


@service(provides=FromRequest[Query])
class QueryFromRequest(FromRequest[Query]):
    async def from_request(self, context: RequestContext) -> Headers:
        return context.query
