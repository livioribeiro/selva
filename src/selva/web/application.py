import asyncio
import functools
import inspect
import logging
import os
from collections.abc import Callable, Iterable
from http import HTTPStatus
from types import ModuleType
from typing import Any, TypeGuard

from asgikit.responses import HttpResponse

from selva.configuration import Settings
from selva.di import Container
from selva.di.decorators import DI_SERVICE_ATTRIBUTE
from selva.utils.base_types import get_base_types
from selva.utils.maybe_async import maybe_async
from selva.utils.package_scan import scan_packages
from selva.web.errors import HttpError
from selva.web.middleware import Middleware
from selva.web.request import RequestContext, from_request_impl
from selva.web.request.from_request import FromRequest
from selva.web.response import into_response_impl
from selva.web.response.into_response import IntoResponse
from selva.web.routing import path_converter_impl
from selva.web.routing.decorators import CONTROLLER_ATTRIBUTE
from selva.web.routing.path_converter import PathConverter
from selva.web.routing.router import Router

MIDDLEWARE_SETTINGS_ATTRIBUTE = "SELVA__MIDDLEWARE_CLASSES"

LOGGER = logging.getLogger(__name__)


@functools.cache
def _selva_environment() -> str | None:
    return os.getenv("SELVA_ENV", None)


@functools.cache
def _selva_debug() -> bool:
    return os.getenv("DEBUG", None) in ("1", "true", "True")


def _is_controller(arg) -> bool:
    return inspect.isclass(arg) and hasattr(arg, CONTROLLER_ATTRIBUTE)


def _is_service(arg) -> bool:
    return hasattr(arg, DI_SERVICE_ATTRIBUTE)


def _is_middleware(arg) -> TypeGuard[Middleware]:
    return inspect.isclass(arg) and issubclass(arg, Middleware)


def _is_module(arg) -> bool:
    return inspect.ismodule(arg) or isinstance(arg, str)


def _is_registerable(arg) -> bool:
    return any(i(arg) for i in [_is_controller, _is_service])


def _get_registerables(*args: type | Callable | ModuleType | str) -> Iterable[type]:
    for item in args:
        if _is_module(item):
            for subitem in scan_packages([item], _is_registerable):
                yield subitem
        elif _is_service(item):
            yield item
        else:
            raise ValueError(f"{item} is not a controller, service or application")


background_tasks = set()


class Selva:
    """Entrypoint class for a Selva Application

    Will try to automatically import and register a module called "application".
    Other modules and classes can be registered using the "register" method
    """

    def __init__(
        self,
        *components: type | Callable | ModuleType | str,
    ):
        self.di = Container()
        self.router = Router()
        self.handler = self._process_request

        self.components = list(components)

        self.di.define_singleton(Router, self.router)
        self.di.scan(path_converter_impl, from_request_impl, into_response_impl)

        self.settings = Settings()
        self.di.define_singleton(Settings, self.settings)

        # try to automatically import and register a module called "application"
        try:
            import application as app

            if app not in components or app.__name__ not in components:
                self.components.append(app)
        except ImportError:
            pass

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http" | "websocket":
                await self._handle_request(RequestContext(scope, receive, send))
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError(f"unknown scope '{scope['type']}'")

    async def _initialize(self):
        services: list[type] = []
        controllers: list[type] = []

        for item in _get_registerables(*self.components):
            self.di.service(item)
            if _is_controller(item):
                self.router.route(item)
                controllers.append(item)
            else:
                services.append(item)

        LOGGER.info("Services:")
        for cls in services:
            LOGGER.info(f"- %s %s", cls.__module__, cls.__name__)

        LOGGER.info("Controllers:")
        for cls in controllers:
            LOGGER.info(f"- %s %s", cls.__module__, cls.__name__)

        LOGGER.info("Middlewares:")
        for cls in getattr(self.settings, MIDDLEWARE_SETTINGS_ATTRIBUTE, []):
            middleware: Middleware = await self.di.get(cls)
            LOGGER.info(f"- %s %s", cls.__module__, cls.__name__)
            self.handler = functools.partial(middleware.execute, self.handler)

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
                    await self.di.run_finalizers()
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as err:
                    await send(
                        {"type": "lifespan.shutdown.failed", "message": str(err)}
                    )
                break

    async def _handle_request(self, context: RequestContext):
        if response := await self.handler(context):
            await response(context.request)

        for result in await asyncio.gather(
            *context.delayed_tasks, return_exceptions=True
        ):
            if isinstance(result, Exception):
                LOGGER.exception(result)

    async def _process_request(self, context: RequestContext) -> HttpResponse:
        method = context.method if context.is_http else None
        path = context.path

        match = self.router.match(method, path)

        if not match:
            return HttpResponse.not_found()

        controller = match.route.controller
        action = match.route.action
        path_params = match.params

        try:
            path_params = await self._params_from_path(
                path_params, match.route.path_params
            )
            request_params = await self._params_from_request(
                context, match.route.request_params
            )

            all_params = path_params | request_params
            instance = await self.di.get(controller)
            response = await maybe_async(action, instance, **all_params)

            if context.is_http:
                return await self._into_response(response)
        except HttpError as err:
            return HttpResponse(status=err.status)
        except Exception as err:
            LOGGER.exception(err)
            return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

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

    async def _into_response(self, value: Any | None) -> HttpResponse | None:
        if isinstance(value, HttpResponse):
            return value

        for base in get_base_types(type(value)):
            if converter := await self.di.get(IntoResponse[base], optional=True):
                return await maybe_async(converter.into_response, value)

        raise RuntimeError(
            f"no implementation of '{IntoResponse.__name__}' found for type '{type(value)}'"
        )
