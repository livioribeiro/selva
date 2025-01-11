import uuid

import structlog
from asgikit.requests import Request

from selva.configuration.settings import Settings
from selva.di.container import Container


async def request_id_middleware(app, settings: Settings, di: Container):
    async def handler(scope, receive, send):
        request = Request(scope, receive, send)

        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request["request_id"] = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)

        await app(scope, receive, send)

        structlog.contextvars.unbind_contextvars("request_id")

    return handler
