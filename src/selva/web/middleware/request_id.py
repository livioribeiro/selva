import uuid

import structlog
from asgikit.requests import Request

from selva.web.middleware import CallNext, Middleware


class RequestIdMiddleware(Middleware):
    async def __call__(
        self,
        call_next: CallNext,
        request: Request,
    ):
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        request["request_id"] = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)
        await call_next(request)
        structlog.contextvars.unbind_contextvars("request_id")
