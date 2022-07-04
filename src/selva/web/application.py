import asyncio
import functools
import inspect
import logging
from collections.abc import Callable
from http import HTTPStatus
from types import ModuleType
from typing import Any, Type

from asgikit.responses import HttpResponse

from selva.di import Container
from selva.di.decorators import DI_SERVICE_ATTRIBUTE
from selva.utils.base_types import get_base_types
from selva.utils.maybe_async import maybe_async
from selva.utils.package_scan import scan_packages
from selva.web.background_tasks import BackgroundTasks
from selva.web.configuration import Settings
from selva.web.errors import HttpError
from selva.web.middleware import Middleware
from selva.web.request import FromRequest, RequestContext, from_request_impl
from selva.web.response import IntoResponse, into_response_impl
from selva.web.routing import param_converter
from selva.web.routing.decorators import CONTROLLER_ATTRIBUTE
from selva.web.routing.router import Router

LOGGER = logging.getLogger(__name__)


def _is_controller(arg) -> bool:
    return inspect.isclass(arg) and hasattr(arg, CONTROLLER_ATTRIBUTE)


def _is_service(arg) -> bool:
    return hasattr(arg, DI_SERVICE_ATTRIBUTE)


def _is_module(arg) -> bool:
    return inspect.ismodule(arg) or isinstance(arg, str)


def _is_registerable(arg) -> bool:
    return any(i(arg) for i in [_is_controller, _is_service])


background_tasks = set()


class Application:
    """Entrypoint class for a Selva Application

    Will try to automatically import and register a application called "application".
    Other modules and classes can be registered using the "register" method
    """

    def __init__(
        self,
        *components,
        middleware: list[Type[Middleware]] = None,
        debug=False,
    ):
        self.debug = debug
        self.di = Container()
        self.router = Router()
        self.handler = self._process_request
        self.middleware_classes: list[Type[Middleware]] = middleware or []

        self.di.define_singleton(Router, self.router)
        self.di.scan(from_request_impl, param_converter, into_response_impl)
        self.di.service(BackgroundTasks)

        self.di.define_singleton(Settings, Settings())

        for mid in self.middleware_classes:
            self.di.register(mid)

        components = set(components)

        # try to automatically import and register a application called "application"
        try:
            import application as app
        except ImportError:
            app = None

        if app and (app not in components or app.__name__ not in components):
            components.add(app)

        self._register(*components)

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http" | "websocket":
                await self._handle_request(RequestContext(scope, receive, send))
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError(f"unknown scope '{scope['type']}'")

    def _register(self, *args: type | Callable | ModuleType | str):
        for item in args:
            if _is_service(item):
                self.di.service(item)
                if _is_controller(item):
                    self.router.route(item)
            elif _is_module(item):
                for subitem in scan_packages([item], _is_registerable):
                    if _is_service(subitem):
                        self.di.service(subitem)
                        if _is_controller(subitem):
                            self.router.route(subitem)
            else:
                raise ValueError(f"{item} is not a controller, service or application")

    async def _handle_lifespan(self, _scope, receive, send):
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
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
                    f"no implementation of 'FromRequest' found for type {item_type}"
                )

        return request_params

    async def _handle_request(self, context: RequestContext):
        for cls in self.middleware_classes:
            middleware = await self.di.get(cls)
            self.handler = functools.partial(middleware.execute, self.handler)

        Application._handle_request = Application._initialized_handle_request

        return await self._initialized_handle_request(context)

    async def _initialized_handle_request(self, context: RequestContext):
        try:
            if response := await self.handler(context):
                await response(context.request)
        finally:
            task = asyncio.create_task(self.di.run_finalizers(context))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)

    async def _process_request(self, context: RequestContext) -> HttpResponse:
        self.di.define_dependent(RequestContext, context, context=context)

        method = context.method if context.is_http else None
        path = context.path

        match = self.router.match(method, path)

        if not match:
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        controller = match.route.controller
        action = match.route.action
        path_params = match.params

        try:
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

    async def _into_response(self, value: Any | None) -> HttpResponse | None:
        if isinstance(value, HttpResponse):
            return value

        for base in get_base_types(type(value)):
            if converter := await self.di.get(IntoResponse[base], optional=True):
                return await maybe_async(converter.into_response, value)

        raise RuntimeError(
            f"no implementation of 'IntoResponse' found for type '{type(value)}'"
        )
