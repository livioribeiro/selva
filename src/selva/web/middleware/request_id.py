import uuid

import structlog
from asgikit.requests import Request

from selva.web.middleware import CallNext


async def request_id_middleware(callnext: CallNext, request: Request):
    request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    request["request_id"] = request_id
    structlog.contextvars.bind_contextvars(request_id=request_id)
    await callnext(request)
    structlog.contextvars.unbind_contextvars("request_id")
