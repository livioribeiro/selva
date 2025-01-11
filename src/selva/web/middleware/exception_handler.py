import functools
from functools import cache

import structlog
from asgikit.requests import Request

from selva._util.base_types import get_base_types
from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.web.exception_handler.decorator import ExceptionHandlerType
from selva.web.exception_handler.discover import find_exception_handlers
from selva.web.handler.call import call_handler

logger = structlog.get_logger()


def exception_handler_middleware(app, settings: Settings, di: Container):
    exception_handlers = find_exception_handlers(settings.application)
    return ExceptionHandlerMiddleware(app, di, exception_handlers)


class ExceptionHandlerMiddleware:
    def __init__(self, app, di: Container, exception_handlers):
        self.app = app
        self.di = di
        self.exception_handlers = exception_handlers

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except Exception as err:
            if handler := self._get_exception_handler(err):
                logger.debug(
                    "Handling exception with handler",
                    module=handler.__module__,
                    handler=handler.__qualname__,
                )

                request = Request(scope, receive, send)
                await call_handler(
                    self.di, functools.partial(handler, err), request, skip=2
                )
            else:
                raise

    @cache
    def _get_exception_handler(self, err: BaseException) -> ExceptionHandlerType | None:
        err_type = type(err)
        for base in get_base_types(err_type):
            if handler := self.exception_handlers.get(base):
                return handler

        return None
