import uuid

import structlog

from selva.conf.settings import Settings
from selva.di.container import Container
from selva.web.http import Request


async def request_id_middleware(app, _settings: Settings, _di: Container):
    async def handler(scope, receive, send):
        request = Request(scope, receive, send)

        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state["request_id"] = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)

        await app(scope, receive, send)

        structlog.contextvars.unbind_contextvars("request_id")
        del request.state["request_id"]

    return handler
