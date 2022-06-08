from typing import Any, Optional, Protocol

from selva.web.request import RequestContext


class Middleware(Protocol):
    async def process_request(self, context: RequestContext) -> Optional[Any]:
        pass

    async def process_response(self, context: RequestContext, result: Any) -> Any:
        pass
