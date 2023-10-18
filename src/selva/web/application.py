import functools
import importlib
import inspect
import logging
import typing
from http import HTTPStatus
from types import FunctionType, ModuleType
from typing import Any

from asgikit.errors.websocket import WebSocketDisconnectError, WebSocketError
from asgikit.requests import Request
from asgikit.responses import Response, respond_status
from asgikit.websockets import WebSocket

from selva._util.base_types import get_base_types
from selva._util.maybe_async import maybe_async
from selva.configuration.logging import setup_logging
from selva.configuration.settings import Settings, get_settings
from selva.di.container import Container
from selva.di.decorator import DI_SERVICE_ATTRIBUTE
from selva.web.converter import (
    from_request_impl,
    param_converter_impl,
    param_extractor_impl,
)
from selva.web.converter.error import (
    MissingFromRequestImplError,
    MissingFromRequestParamImplError,
    MissingRequestParamExtractorImplError,
)
from selva.web.converter.from_request import FromRequest
from selva.web.converter.param_converter import ParamConverter
from selva.web.converter.param_extractor import RequestParamExtractor
from selva.web.exception import HTTPException, HTTPNotFoundException, WebSocketException
from selva.web.exception_handler import ExceptionHandler
from selva.web.middleware import Middleware
from selva.web.routing.decorator import CONTROLLER_ATTRIBUTE
from selva.web.routing.router import Router

logger = logging.getLogger(__name__)


def _is_controller(arg) -> bool:
    return inspect.isclass(arg) and hasattr(arg, CONTROLLER_ATTRIBUTE)


def _is_service(arg) -> bool:
    return hasattr(arg, DI_SERVICE_ATTRIBUTE)


def _is_module(arg) -> bool:
    return inspect.ismodule(arg) or isinstance(arg, str)


class Selva:
    """Entrypoint class for a Selva Application

    Will try to automatically import and register a module called "application".
    Other modules and classes can be registered using the "register" method
    """

    def __init__(self):
        self.di = Container()
        self.router = Router()
        self.handler = self._process_request

        self.settings = get_settings()
        self.di.define(Settings, self.settings)

        setup_logging(self.settings)

        self.di.define(Router, self.router)

        self.di.scan(
            from_request_impl,
            param_extractor_impl,
            param_converter_impl,
        )
        self.di.scan(self.settings.COMPONENTS)

        components = self.settings.COMPONENTS
        self._register_components(components)

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http" | "websocket":
                await self._handle_request(scope, receive, send)
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError(f"unknown scope '{scope['type']}'")

    def _register_components(
        self, components: list[str | ModuleType | type | FunctionType]
    ):
        try:
            app = importlib.import_module("application")

            if app not in components or app.__name__ not in components:
                components.append(app)
        except ImportError as err:
            if err.name != "application":
                raise

        services = []
        packages = []

        for component in components:
            if _is_service(component):
                services.append(component)
            elif _is_module(component):
                packages.append(component)
            else:
                raise TypeError(f"Invalid component: {component}")

        self.di.scan(*packages)

        for service in services:
            self.di.service(service)

        for _iface, impl, _name in self.di.iter_all_services():
            if _is_controller(impl):
                self.router.route(impl)

    async def _initialize_middleware(self):
        middleware = self.settings.MIDDLEWARE
        if len(middleware) == 0:
            return

        if middleware_errors := [
            m for m in middleware if not issubclass(m, Middleware)
        ]:
            mid_classes = [
                f"{m.__module__}.{m.__qualname__}" for m in middleware_errors
            ]
            mid_class_name = f"{Middleware.__module__}.{Middleware.__qualname__}"
            raise TypeError(
                f"Middleware classes must inherit from '{mid_class_name}': {mid_classes}"
            )

        for cls in reversed(self.settings.MIDDLEWARE):
            mid = await self.di.create(cls)
            chain = functools.partial(mid, self.handler)
            self.handler = chain

    async def _initialize(self):
        await self._initialize_middleware()

    async def _finalize(self):
        await self.di.run_finalizers()

    async def _handle_lifespan(self, _scope, receive, send):
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
                    await self._initialize()
                    await send({"type": "lifespan.startup.complete"})
                except Exception as err:
                    await send({"type": "lifespan.startup.failed", "message": str(err)})
            elif message["type"] == "lifespan.shutdown":
                try:
                    await self._finalize()
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as err:
                    await send(
                        {"type": "lifespan.shutdown.failed", "message": str(err)}
                    )
                break

    async def _handle_request(self, scope, receive, send):
        request = Request(scope, receive, send)
        response = Response(scope, receive, send)

        try:
            try:
                await self.handler(request, response)
            except Exception as err:
                if handler := await self.di.get(
                    ExceptionHandler[type(err)], optional=True
                ):
                    await handler.handle_exception(request, response, err)
                else:
                    raise
        except WebSocketException as err:
            await request.websocket.close(err.code, err.reason)
        except (WebSocketDisconnectError, WebSocketError):
            logger.exception("WebSocket error")
            await request.websocket.close()
        except HTTPException as err:
            if response.is_started:
                logger.error("Response has already started")
                await response.end()
                return

            if response.is_finished:
                logger.error("Response is finished")
                return

            await respond_status(response, err.status)
        except Exception as err:
            logger.exception("Error processing request", exc_info=err)
            await respond_status(response, HTTPStatus.INTERNAL_SERVER_ERROR)

    async def _process_request(self, request: Request, response: Response):
        method = request.method
        path = request.path

        match = self.router.match(method, path)

        if not match:
            raise HTTPNotFoundException()

        controller = match.route.controller
        action = match.route.action
        path_params = match.params

        path_params = await self._params_from_path(path_params, match.route.path_params)

        request_params = await self._params_from_request(
            request, match.route.request_params
        )

        all_params = path_params | request_params
        instance = await self.di.get(controller)
        await action(instance, request, response, **all_params)

        if ws := request.websocket:
            if ws.state != WebSocket.State.CLOSED:
                logger.warning("closing websocket")
                await ws.close()
        elif not response.is_started:
            await respond_status(response, HTTPStatus.INTERNAL_SERVER_ERROR)
        elif not response.is_finished:
            await response.end()

    async def _params_from_path(
        self,
        values: dict[str, str],
        params: dict[str, type],
    ) -> dict[str, Any]:
        result = {}

        for name, param_type in params.items():
            if param_type is str:
                result[name] = values[name]
                continue

            if converter := await self._find_param_converter(
                param_type, ParamConverter
            ):
                value = await maybe_async(converter.from_param, values[name])
                result[name] = value
            else:
                raise MissingFromRequestParamImplError(param_type)

        return result

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
                    RequestParamExtractor[extractor_type], optional=True
                )
                if not extractor:
                    raise MissingRequestParamExtractorImplError(extractor_type)

                param = extractor.extract(request, name, extractor_param)
                if not param:
                    continue

                if converter := await self._find_param_converter(
                    param_type, ParamConverter
                ):
                    value = await maybe_async(converter.from_param, param)
                    result[name] = value
                else:
                    raise MissingFromRequestParamImplError(param_type)
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
