import importlib
import inspect
from collections import OrderedDict
from collections.abc import Callable, Coroutine
from types import ModuleType
from typing import Any

from asgikit.responses import HttpResponse, HTTPStatus

from selva.di import Container
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
        self.middleware_chain = OrderedDict()

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http" | "websocket":
                await self._handle_request(RequestContext(scope, receive, send))
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError()

    def register(self, *args: type | Callable | ModuleType | str):
        for item in args:
            if _is_controller(item):
                self.router.route(item)
            if _is_service(item):
                self.di.service(item)
            if _is_middleware(item):
                self.middleware_chain[item] = None
            if inspect.ismodule(item) or isinstance(item, str):
                for i in package_scan.scan_packages(
                    [item], _is_controller_or_service_or_middleware
                ):
                    self.register(i)

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
        chain = Chain(self.di, self.middleware_chain, self._process_request, context)

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
        except Exception as err:
            print(err)
            response = HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return response
