import importlib
import inspect
import logging
from http import HTTPStatus
from types import FunctionType, ModuleType
from typing import Any

from starlette.exceptions import HTTPException, WebSocketException
from starlette.responses import Response
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocketClose, WebSocketDisconnect, WebSocketState

from selva._utils.base_types import get_base_types
from selva._utils.maybe_async import maybe_async
from selva.configuration.logging import setup_logging
from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.di.decorators import DI_SERVICE_ATTRIBUTE
from selva.web.contexts import RequestContext
from selva.web.converter import (
    from_request_impl,
    into_response_impl,
    path_converter_impl,
)
from selva.web.converter.from_request import FromRequest
from selva.web.converter.into_response import IntoResponse
from selva.web.converter.path_converter import PathConverter
from selva.web.errors import HTTPNotFoundError
from selva.web.middleware import Middleware
from selva.web.routing.decorators import CONTROLLER_ATTRIBUTE
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

        self.settings = Settings()
        setup_logging(self.settings)

        self.di.define(Settings, self.settings)
        self.di.define(Router, self.router)

        self.di.scan(path_converter_impl, from_request_impl, into_response_impl)
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
        except ImportError:
            pass

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
            mid.set_app(self.handler)
            self.handler = mid

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

    async def _handle_request(self, scope: Scope, receive: Receive, send: Send):
        context = RequestContext(scope, receive, send)

        try:
            if response := await self.handler(context):
                await response(scope, receive, send)
        except (WebSocketException, WebSocketDisconnect) as err:
            await WebSocketClose(code=err.code, reason=err.reason)(scope, receive, send)
        except HTTPException as err:
            await Response(status_code=err.status_code)(scope, receive, send)
        except Exception as err:
            logger.exception("Error processing request", exc_info=err)
            await Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)(
                scope, receive, send
            )

    async def _process_request(
        self, context: RequestContext
    ) -> Response | WebSocketClose:
        method = context.method
        path = context.path

        match = self.router.match(method, path)

        if not match:
            raise HTTPNotFoundError()

        controller = match.route.controller
        action = match.route.action
        path_params = match.params

        path_params = await self._params_from_path(path_params, match.route.path_params)
        request_params = await self._params_from_request(
            context, match.route.request_params
        )

        all_params = path_params | request_params
        instance = await self.di.get(controller)
        response = await maybe_async(action, instance, **all_params)

        if context.is_websocket:
            if (
                not response
                and context.websocket._inner.client_state != WebSocketState.DISCONNECTED
            ):
                response = WebSocketClose()
        else:
            response = await self._into_response(response)

        return response

    async def _params_from_path(
        self,
        values: dict[str, str],
        params: dict[str, type],
    ) -> dict[str, Any]:
        path_params = {}

        for name, item_type in params.items():
            for base_type in get_base_types(item_type):
                if converter := await self.di.get(
                    PathConverter[base_type], optional=True
                ):
                    value = await maybe_async(converter.from_path, values[name])
                    path_params[name] = value
                    break
            else:
                raise RuntimeError(
                    f"no implementation of '{PathConverter.__name__}' found for type {item_type}"
                )

        return path_params

    async def _params_from_request(
        self,
        context: RequestContext,
        params: dict[str, type],
    ) -> dict[str, Any]:
        request_params = {}

        for name, item_type in params.items():
            for base_type in get_base_types(item_type):
                if converter := await self.di.get(
                    FromRequest[base_type], optional=True
                ):
                    value = await maybe_async(converter.from_request, context)
                    request_params[name] = value
                    break
            else:
                raise RuntimeError(
                    f"no implementation of '{FromRequest.__name__}' found for type {item_type}"
                )

        return request_params

    async def _into_response(self, value: Any | None) -> Response | None:
        if isinstance(value, Response):
            return value

        for base in get_base_types(type(value)):
            if converter := await self.di.get(IntoResponse[base], optional=True):
                return await maybe_async(converter.into_response, value)

        raise RuntimeError(
            f"no implementation of '{IntoResponse.__name__}' found for type '{type(value)}'"
        )
