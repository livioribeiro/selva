import functools
import inspect
import traceback
import typing
from collections.abc import Callable
from functools import cache
from http import HTTPStatus
from typing import Any

import structlog
from asgikit.errors.websocket import WebSocketDisconnectError, WebSocketError
from asgikit.requests import Request
from asgikit.responses import respond_status, respond_text
from asgikit.websockets import WebSocket

from selva._util.base_types import get_base_types
from selva._util.import_item import import_item
from selva._util.maybe_async import maybe_async
from selva._util.package_scan import scan_packages
from selva.configuration.settings import Settings, get_settings
from selva.di.container import Container
from selva.di.decorator import ATTRIBUTE_DI_SERVICE
from selva.ext.error import ExtensionNotFoundError, ExtensionMissingInitFunctionError
from selva.web.converter.error import MissingFromRequestImplError
from selva.web.converter.from_request import FromRequest
from selva.web.exception import HTTPException, HTTPNotFoundException, WebSocketException
from selva.web.exception_handler import (
    ATTRIBUTE_EXCEPTION_HANDLER,
    ExceptionHandlerType,
)
from selva.web.handler import parse_handler_params
from selva.web.routing.decorator import ATTRIBUTE_HANDLER
from selva.web.routing.router import Router

logger = structlog.get_logger()


def _is_handler(arg) -> bool:
    return inspect.iscoroutinefunction(arg) and hasattr(arg, ATTRIBUTE_HANDLER)


def _is_exception_handler(arg) -> bool:
    return inspect.iscoroutinefunction(arg) and hasattr(
        arg, ATTRIBUTE_EXCEPTION_HANDLER
    )


def _is_service(arg) -> bool:
    return (inspect.isfunction(arg) or inspect.isclass(arg)) and hasattr(
        arg, ATTRIBUTE_DI_SERVICE
    )


def _init_settings(settings: Settings | None) -> Settings:
    if not settings:
        settings, paths = get_settings()

    logging_setup = import_item(settings.logging.setup)
    logging_setup(settings)

    return settings


class Selva:
    """Entrypoint class for a Selva Application

    Will try to automatically import and register a module called "application".
    Other modules and classes can be registered using the "register" method
    """

    def __init__(self, settings: Settings = None):
        self.settings = _init_settings(settings)

        self.di = Container()
        self.di.define(Container, self.di)

        self.di.define(Settings, self.settings)

        self.router = Router()
        self.di.define(Router, self.router)

        self.handler = self._request_handler
        self.exception_handlers: dict[type[BaseException], ExceptionHandlerType] = {}

        self._register_modules()

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http" | "websocket":
                await self._handle_request(scope, receive, send)
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError(f"unknown scope '{scope['type']}'")

    def _register_modules(self):
        packages_to_scan = [
            self.settings.application,
            "selva.web.converter",
            "selva.web.middleware",
        ]

        for item in scan_packages(packages_to_scan):
            if _is_handler(item):
                self.router.route(item)

            if _is_exception_handler(item):
                exc_handler_info = getattr(item, ATTRIBUTE_EXCEPTION_HANDLER)
                exc_type = exc_handler_info.exception_class
                if exc_type in self.exception_handlers:
                    raise ValueError("Exception handler already registered")

                self.exception_handlers[exc_type] = item

            if _is_service(item):
                self.di.register(item)

    async def _initialize_extensions(self):
        for extension_name in self.settings.extensions:
            try:
                extension_module = import_item(extension_name)
            except ImportError:
                # pylint: disable=raise-missing-from
                raise ExtensionNotFoundError(extension_name)

            extension_init = getattr(extension_module, "init_extension", None)
            if not extension_init:
                raise ExtensionMissingInitFunctionError(extension_name)

            await maybe_async(extension_init, self.di, self.settings)

    async def _initialize_middleware(self):
        middleware = self.settings.middleware
        if not middleware:
            return

        middleware_functions = [import_item(name) for name in middleware]

        for mid in reversed(middleware_functions):
            self.handler = functools.partial(
                self._call_handler, functools.partial(mid, self.handler), skip=2
            )

    async def _lifespan_startup(self):
        await self.di.init_startup_services()
        await self._initialize_extensions()
        await self._initialize_middleware()

    async def _lifespan_shutdown(self):
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
        request = Request(scope, receive, send)

        try:
            try:
                await self.handler(request)
            except Exception as err:
                if handler := self._find_exception_handler(type(err)):
                    logger.debug(
                        "Handling exception with handler",
                        module=handler.__module__,
                        handler=handler.__qualname__,
                    )
                    await self._call_handler(
                        functools.partial(handler, err), request, skip=2
                    )
                else:
                    raise
        except (WebSocketDisconnectError, WebSocketError):
            logger.exception("websocket error")
            await request.websocket.close()
        except WebSocketException as err:
            await request.websocket.close(err.code, err.reason)
        except HTTPException as err:
            if websocket := request.websocket:
                logger.exception("websocket request raised HTTPException")
                await websocket.close()
                return

            response = request.response

            if cause := err.__cause__:
                logger.exception(cause)
                stack_trace = "".join(traceback.format_exception(cause))
            else:
                stack_trace = None

            if response.is_started:
                logger.error("response has already started")
                await response.end()
                return

            if response.is_finished:
                logger.error("response is finished")
                return

            if stack_trace:
                response.status = err.status
                await respond_text(response, stack_trace)
            else:
                await respond_status(response, status=err.status)
        except Exception:
            logger.exception("error processing request")

            request.response.status = HTTPStatus.INTERNAL_SERVER_ERROR
            await respond_text(request.response, traceback.format_exc())

    async def _request_handler(self, request: Request):
        path = request.path

        logger.debug(
            "handling request",
            method=str(request.method),
            path=path,
            query=request.query,
        )

        match = self.router.match(request.method, path)

        if not match:
            raise HTTPNotFoundException()

        action = match.route.action
        path_params = match.params
        request["path_params"] = path_params

        await self._call_handler(action, request, skip=1)

        response = request.response

        if ws := request.websocket:
            if ws.state != WebSocket.State.CLOSED:
                logger.warning("closing websocket")
                await ws.close()
        elif not response.is_started:
            await respond_status(response, HTTPStatus.INTERNAL_SERVER_ERROR)
        elif not response.is_finished:
            await response.end()

    async def _call_handler(self, handler: Callable, request: Request, *, skip: int):
        actual_handler = handler
        while isinstance(actual_handler, functools.partial):
            actual_handler = actual_handler.func

        handler_params = parse_handler_params(actual_handler, skip=skip)
        request_params = await self._params_from_request(
            request, handler_params.request
        )
        request_services = {
            name: await self.di.get(
                service_type, name=service_name, optional=has_default
            )
            for name, (
                service_type,
                service_name,
                has_default,
            ) in handler_params.service
        }

        await handler(request, **(request_params | request_services))

    async def _params_from_request(
        self,
        request: Request,
        params: list[tuple[str, Any, bool]],
    ) -> dict[str, Any]:
        result = {}

        for name, (param_type, param_annotation, has_default) in params:
            if param_annotation:
                if inspect.isclass(param_annotation):
                    converter_type = param_annotation
                else:
                    converter_type = type(param_annotation)
            else:
                converter_type = param_type

            if from_request_service := await self.di.get(FromRequest[converter_type]):
                value = await maybe_async(
                    from_request_service.from_request,
                    request,
                    param_type,
                    name,
                    param_annotation,
                    has_default,
                )

                if value:
                    result[name] = value
            else:
                raise MissingFromRequestImplError(param_type)

        return result

    @cache
    def _find_exception_handler(
        self, err: type[BaseException]
    ) -> ExceptionHandlerType | None:
        for base in get_base_types(err):
            if handler := self.exception_handlers.get(base):
                return handler

        return None

    @cache
    async def _find_from_request_converter(self, param_type: type) -> Any | None:
        if typing.get_origin(param_type) is list:
            (param_type,) = typing.get_args(param_type)
            is_generic = True
        else:
            is_generic = False

        for base_type in get_base_types(param_type):
            search_type = list[base_type] if is_generic else base_type
            if converter := await self.di.get(FromRequest[search_type], optional=True):
                return converter

        return None
