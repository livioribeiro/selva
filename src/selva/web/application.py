import functools
import inspect
import typing
from http import HTTPStatus
from typing import Any
from uuid import uuid4

from asgikit.errors.websocket import WebSocketDisconnectError, WebSocketError
from asgikit.requests import Request
from asgikit.responses import respond_status, respond_text
from asgikit.websockets import WebSocket
from loguru import logger

from selva._util.base_types import get_base_types
from selva._util.import_item import import_item
from selva._util.maybe_async import maybe_async
from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.web.converter import (
    from_request_impl,
    param_converter_impl,
    param_extractor_impl,
)
from selva.web.converter.error import (
    MissingFromRequestImplError,
    MissingParamConverterImplError,
    MissingRequestParamExtractorImplError,
)
from selva.web.converter.from_request import FromRequest
from selva.web.converter.param_converter import ParamConverter
from selva.web.converter.param_extractor import ParamExtractor
from selva.web.exception import HTTPException, HTTPNotFoundException, WebSocketException
from selva.web.exception_handler import ExceptionHandler
from selva.web.middleware import Middleware
from selva.web.routing.decorator import CONTROLLER_ATTRIBUTE
from selva.web.routing.router import Router


def _is_controller(arg) -> bool:
    return inspect.isclass(arg) and hasattr(arg, CONTROLLER_ATTRIBUTE)


def _is_module(arg) -> bool:
    return inspect.ismodule(arg) or isinstance(arg, str)


class Selva:
    """Entrypoint class for a Selva Application

    Will try to automatically import and register a module called "application".
    Other modules and classes can be registered using the "register" method
    """

    def __init__(self, settings: Settings):
        self.di = Container()
        self.di.define(Container, self.di)

        self.router = Router()
        self.di.define(Router, self.router)

        self.settings = settings
        self.di.define(Settings, self.settings)

        self.handler = self._process_request

        self._register_modules()

        setup_logger = import_item(self.settings.logging.setup)
        setup_logger(self.settings)

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http" | "websocket":
                with logger.contextualize(request_id=uuid4()):
                    await self._handle_request(scope, receive, send)
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError(f"unknown scope '{scope['type']}'")

    def _register_modules(self):
        self.di.scan()

        self.di.scan(
            from_request_impl,
            param_extractor_impl,
            param_converter_impl,
        )

        self.di.scan(self.settings.application)

        for _iface, impl, _name in self.di.iter_all_services():
            if _is_controller(impl):
                self.router.route(impl)

    async def _initialize_extensions(self):
        for extension_name in self.settings.extensions:
            try:
                extension_module = import_item(extension_name)
            except ImportError:
                raise TypeError(f"Extension '{extension_name}' not found")

            try:
                extension_init = getattr(extension_module, "selva_extension")
            except AttributeError:
                raise TypeError(
                    f"Extension '{extension_name}' is missing the 'selva_extension()' function"
                )

            await maybe_async(extension_init, self.di, self.settings)

    async def _initialize_middleware(self):
        middleware = self.settings.middleware
        if len(middleware) == 0:
            return

        middleware = [import_item(name) for name in middleware]

        if errors := [m for m in middleware if not issubclass(m, Middleware)]:
            mid_classes = [f"{m.__module__}.{m.__qualname__}" for m in errors]
            mid_class_name = f"{Middleware.__module__}.{Middleware.__qualname__}"
            raise TypeError(
                f"Middleware classes must be of type '{mid_class_name}': {mid_classes}"
            )

        for cls in reversed(middleware):
            mid = await self.di.get(cls)
            chain = functools.partial(mid, self.handler)
            self.handler = chain

    async def _lifespan_startup(self):
        await self.di._run_startup()
        await self._initialize_extensions()
        await self._initialize_middleware()

    async def _lifespan_shutdown(self):
        await self.di._run_finalizers()

    async def _handle_lifespan(self, _scope, receive, send):
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                logger.trace("Handling lifespan startup")
                try:
                    await self._lifespan_startup()
                    logger.trace("Lifespan startup complete")
                    await send({"type": "lifespan.startup.complete"})
                except Exception as err:
                    logger.trace("Lifespan startup failed")
                    await send({"type": "lifespan.startup.failed", "message": str(err)})
            elif message["type"] == "lifespan.shutdown":
                logger.trace("Handling lifespan shutdown")
                try:
                    await self._lifespan_shutdown()
                    logger.trace("Lifespan shutdown complete")
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as err:
                    logger.trace("Lifespan shutdown failed")
                    await send(
                        {"type": "lifespan.shutdown.failed", "message": str(err)}
                    )
                break

    async def _handle_request(self, scope, receive, send):
        request = Request(scope, receive, send)

        logger.trace(
            "Started handling of request '{} {} {}'",
            request.method,
            request.path,
            request.raw_query,
        )

        try:
            try:
                await self.handler(request)
            except Exception as err:
                if handler := await self.di.get(
                    ExceptionHandler[type(err)], optional=True
                ):
                    logger.trace(
                        "Handling exception with handler {}.{}",
                        handler.__class__.__module__,
                        handler.__class__.__qualname__,
                    )
                    await handler.handle_exception(request, err)
                else:
                    raise
        except WebSocketException as err:
            await request.websocket.close(err.code, err.reason)
        except (WebSocketDisconnectError, WebSocketError):
            logger.exception("WebSocket error")
            await request.websocket.close()
        except HTTPException as err:
            if websocket := request.websocket:
                logger.error("WebSocket request raise HTTPException")
                await websocket.close()
            else:
                response = request.response
                if response.is_started:
                    logger.error("Response has already started")
                    await response.end()
                    return

                if response.is_finished:
                    logger.error("Response is finished")
                    return

                await respond_text(response, str(err), status=err.status)
        except Exception as err:
            logger.exception("Error processing request")
            await respond_text(
                request.response, str(err), status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    async def _process_request(self, request: Request):
        method = request.method
        path = request.path

        match = self.router.match(method, path)

        if not match:
            raise HTTPNotFoundException()

        controller = match.route.controller
        action = match.route.action
        path_params = match.params
        request["path_params"] = path_params

        request_params = await self._params_from_request(
            request, match.route.request_params
        )

        instance = await self.di.get(controller)
        await action(instance, request, **request_params)

        response = request.response

        if ws := request.websocket:
            if ws.state != WebSocket.State.CLOSED:
                logger.warning("closing websocket")
                await ws.close()
        elif not response.is_started:
            await respond_status(response, HTTPStatus.INTERNAL_SERVER_ERROR)
        elif not response.is_finished:
            await response.end()

    async def _params_from_request(
        self,
        request: Request,
        params: dict[str, type],
    ) -> dict[str, Any]:
        result = {}

        for name, (param_type, extractor_param) in params.items():
            if extractor_param:
                if inspect.isclass(extractor_param):
                    extractor_type = extractor_param
                else:
                    extractor_type = type(extractor_param)

                extractor = await self.di.get(
                    ParamExtractor[extractor_type], optional=True
                )
                if not extractor:
                    raise MissingRequestParamExtractorImplError(extractor_type)

                param = extractor.extract(request, name, extractor_param)
                if not param:
                    continue

                if converter := await self._find_param_converter(
                    param_type, ParamConverter
                ):
                    value = await maybe_async(converter.from_str, param)
                    result[name] = value
                else:
                    raise MissingParamConverterImplError(param_type)
            else:
                if converter := await self._find_param_converter(
                    param_type, FromRequest
                ):
                    value = await maybe_async(
                        converter.from_request, request, param_type, name
                    )
                    result[name] = value
                else:
                    raise MissingFromRequestImplError(param_type)

        return result

    async def _find_param_converter(
        self, param_type: type, converter_type: type
    ) -> Any | None:
        if typing.get_origin(param_type) is list:
            (param_type,) = typing.get_args(param_type)
            is_generic = True
        else:
            is_generic = False

        for base_type in get_base_types(param_type):
            search_type = list[base_type] if is_generic else base_type
            if converter := await self.di.get(
                converter_type[search_type], optional=True
            ):
                return converter

        return None
