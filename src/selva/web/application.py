import inspect
from collections import OrderedDict
from collections.abc import Callable, Coroutine
from types import ModuleType
from typing import Any

from asgikit.responses import HttpResponse, HTTPStatus

from selva.di import Container, Scope
from selva.di.decorators import DI_SERVICE_ATTRIBUTE
from selva.utils import maybe_async, package_scan
from selva.web.middleware.chain import Chain
from selva.web.middleware.decorators import MIDDLEWARE_ATTRIBUTE
from selva.web.request import FromRequestContext, RequestContext, from_context
from selva.web.routing import param_converter
from selva.web.routing.decorators import CONTROLLER_ATTRIBUTE
from selva.web.routing.router import Router


def _is_controller(arg) -> bool:
    return inspect.isclass(arg) and hasattr(arg, CONTROLLER_ATTRIBUTE)


def _is_service(arg) -> bool:
    return hasattr(arg, DI_SERVICE_ATTRIBUTE)


def _is_middleware(arg) -> bool:
    return hasattr(arg, MIDDLEWARE_ATTRIBUTE)


def _is_controller_or_service_or_middleware(arg) -> bool:
    return any(i(arg) for i in [_is_controller, _is_service, _is_middleware])


class Application:
    def __init__(
        self,
        *,
        debug=False,
    ):
        self.debug = debug
        self.di = Container()
        self.router = Router()

        self.di.define_singleton(Router, self.router)
        self.di.scan(from_context, param_converter)
        self.middleware_classes = OrderedDict()
        self.middleware_chain = None

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http" | "websocket":
                await self._handle_request(RequestContext(scope, receive, send))
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError(f"unknown scope '{scope['type']}'")

    def register(self, *args: type | Callable | ModuleType | str):
        for item in args:
            if _is_controller(item):
                self.router.route(item)
            elif _is_service(item):
                self.di.service(item)
            elif _is_middleware(item):
                self.middleware_classes[item] = None
                # Middleware execution order is defined by the declaration order in the
                # Application.register method, therefore when a middleware is found, it
                # is put at the chain to override the order or middlewares found in the
                # modules provided to the Application.register method
                self.middleware_classes.move_to_end(item)
                self.di.register(item, Scope.SINGLETON)
            elif inspect.ismodule(item) or isinstance(item, str):
                for subitem in package_scan.scan_packages(
                    [item], _is_controller_or_service_or_middleware
                ):
                    if _is_controller(subitem):
                        self.router.route(subitem)
                    elif _is_service(subitem):
                        self.di.service(subitem)
                    elif _is_middleware(subitem):
                        self.middleware_classes[subitem] = None
                        # Middlewares found in modules are ordered as they are found
                        self.di.register(item, Scope.SINGLETON)
            else:
                raise ValueError(f"{item} is not a controller, service or module")

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

    async def _get_params_from_context(
        self,
        context: RequestContext,
        params: dict[str, type],
    ) -> dict[str, Any]:
        request_params = {}

        for name, item_type in params.items():
            converter = await self.di.get(FromRequestContext[item_type])
            value = await converter.from_context(context)
            request_params[name] = value

        return request_params

    async def _handle_request(self, context: RequestContext):
        if not self.middleware_chain:
            self.middleware_chain = [
                await self.di.get(cls) for cls in self.middleware_classes.keys()
            ]

        chain = Chain(self.middleware_chain, self._process_request, context)

        try:
            if response := await chain():
                await response(context.request)
        finally:
            await self.di.run_finalizers(context)

    async def _process_request(self, context: RequestContext) -> Any | Coroutine:
        self.di.define_dependent(RequestContext, context, context=context)

        method = context.method if context.is_http else None
        path = context.path

        match = self.router.match(method, path)

        if not match:
            response = HttpResponse(status=HTTPStatus.NOT_FOUND)
            return response

        controller = match.route.controller
        action = match.route.action
        path_params = match.params
        request_params = await self._get_params_from_context(
            context, match.route.request_params
        )

        all_params = path_params | request_params

        try:
            instance = await self.di.create(controller, context=context)

            response = await maybe_async.call_maybe_async(
                action, instance, **all_params
            )

            if context.is_http:
                return response
        except Exception:
            response = HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return response
