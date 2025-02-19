import asyncio
import traceback
from http import HTTPStatus

import structlog
from starlette.responses import PlainTextResponse
from starlette.websockets import WebSocketState, WebSocketDisconnect

from selva.web.http import Request, WebSocket, Response

from selva._util.import_item import import_item
from selva._util.maybe_async import maybe_async
from selva.conf.settings import Settings, get_settings
from selva.di.call import call_with_dependencies
from selva.di.container import Container
from selva.ext.error import ExtensionMissingInitFunctionError, ExtensionNotFoundError
from selva.web.exception import HTTPException, HTTPNotFoundException, WebSocketException
from selva.web.exception_handler.discover import find_exception_handlers
from selva.web.handler.call import call_handler
from selva.web.lifecycle.discover import find_background_services, find_startup_hooks
from selva.web.middleware.exception_handler import exception_handler_middleware
from selva.web.routing.router import Router

logger = structlog.get_logger()


def _init_settings(settings: Settings | None) -> Settings:
    settings_files = []
    if not settings:
        settings, settings_files = get_settings()

    logging_setup = import_item(settings.logging.setup)
    logging_setup(settings)

    for settings_file, profile, found in settings_files:
        if found:
            logger.info("settings loaded", settings_file=settings_file)
        elif profile:
            logger.warning("settings file not found", settings_file=settings_file)

    return settings


class Selva:
    """Entrypoint class for a Selva Application

    Will try to automatically import and register a module called "application".
    Other modules and classes can be registered using the "register" method
    """

    def __init__(self, settings: Settings = None, container: Container = None):
        self.settings = _init_settings(settings)

        self.di = Container() if not container else container
        self.di.define(Container, self.di)

        self.di.define(Settings, self.settings)

        self.router = Router()
        self.di.define(Router, self.router)

        self.handler = self._request_handler
        self.exception_handlers = find_exception_handlers(self.settings.application)

        self.startup = find_startup_hooks(self.settings.application)
        self.background_services = find_background_services(self.settings.application)
        self._background_services: set[asyncio.Task] = set()

        self.di.scan(
            self.settings.application,
            "selva.web.converter",
            "selva.web.middleware",
        )
        self.router.scan(self.settings.application)

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http" | "websocket":
                await self._handle_request(scope, receive, send)
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError(f"unknown scope '{scope['type']}'")

    async def _initialize_extensions(self):
        for extension_name in self.settings.extensions:
            try:
                extension_init = import_item(f"{extension_name}:init_extension")
            except ImportError:
                # pylint: disable=raise-missing-from
                raise ExtensionNotFoundError(extension_name)
            except AttributeError:
                # pylint: disable=raise-missing-from
                raise ExtensionMissingInitFunctionError(extension_name)

            await maybe_async(extension_init, self.di, self.settings)

    async def _initialize_middleware(self):
        middleware = self.settings.middleware
        if not middleware:
            middleware_functions = [exception_handler_middleware]
        else:
            middleware_functions = [import_item(name) for name in middleware]
            if exception_handler_middleware in middleware_functions:
                middleware_functions.remove(exception_handler_middleware)

            middleware.append(exception_handler_middleware)

        for factory in reversed(middleware_functions):
            self.handler = await maybe_async(
                factory, self.handler, self.settings, self.di
            )

    async def _lifespan_startup(self):
        await self._initialize_extensions()
        await self._initialize_middleware()

        for hook in self.startup:
            await call_with_dependencies(self.di, hook)

        for hook in self.background_services:
            task = asyncio.create_task(call_with_dependencies(self.di, hook))
            self._background_services.add(task)

            def done_callback(done):
                if err := done.exception():
                    logger.exception(err, exc_info=err)
                self._background_services.discard(done)

            task.add_done_callback(done_callback)

    async def _lifespan_shutdown(self):
        for task in self._background_services:
            if not task.done():
                task.cancel()

        await self.di.run_finalizers()

    async def _handle_lifespan(self, _scope, receive, send):
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                logger.debug("handling lifespan startup")
                try:
                    await self._lifespan_startup()
                    logger.debug("lifespan startup complete")
                    await send({"type": "lifespan.startup.complete"})
                except Exception as err:
                    logger.exception("lifespan startup failed")
                    await send({"type": "lifespan.startup.failed", "message": str(err)})
            elif message["type"] == "lifespan.shutdown":
                logger.debug("handling lifespan shutdown")
                try:
                    await self._lifespan_shutdown()
                    logger.debug("lifespan shutdown complete")
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as err:
                    logger.debug("lifespan shutdown failed")
                    await send(
                        {"type": "lifespan.shutdown.failed", "message": str(err)}
                    )
                break

    async def _handle_request(self, scope, receive, send):
        try:
            await self.handler(scope, receive, send)
        except WebSocketDisconnect:
            logger.info("websocket disconnect", client=scope["client"])
            await send({"type": "websocket.close"})
        except WebSocketException as err:
            await send(
                {
                    "type": "websocket.close",
                    "code": err.code,
                    "reason": err.reason or "",
                }
            )
        except HTTPException as err:
            if scope["type"] == "websocket":
                logger.exception("websocket request raised HTTPException")
                await send({"type": "websocket.close"})
                return

            if cause := err.__cause__:
                logger.exception(cause)
                stack_trace = "".join(traceback.format_exception(cause))
            else:
                stack_trace = None

            if scope["__finished__"]:
                logger.error("request already finished")
                return

            request = Request(scope, receive, send)
            if stack_trace:
                response = PlainTextResponse(stack_trace, status_code=err.status)
                await request.respond(response)
            else:
                await request.respond(err.status)
        except Exception:
            logger.exception("error processing request")

            if scope["type"] == "http":
                status = HTTPStatus.INTERNAL_SERVER_ERROR
                request = Request(scope, receive, send)
                await request.respond(status)
            else:
                await send({"type": "websocket.close"})

    async def _request_handler(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive, send)
            method = request.method

            logger.debug(
                "handling http request",
                method=str(request.method),
                path=request.url.path,
                query=request.query_params,
            )
        else:
            request = WebSocket(scope, receive, send)
            method = None

            logger.debug(
                "handling websocket",
                path=request.url.path,
                query=request.query_params,
            )

        path = request.url.path
        match = self.router.match(method, path)

        if not match:
            raise HTTPNotFoundException()

        action = match.route.action
        path_params = match.params
        request.scope["path_params"] = path_params

        await call_handler(self.di, action, request, skip=1)

        if isinstance(request, WebSocket):
            ws: WebSocket = request
            if ws.client_state != WebSocketState.CONNECTED:
                logger.warning("closing websocket")
                await ws.close()
        elif not request.scope["__finished__"]:
            await request.respond(
                Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
            )
