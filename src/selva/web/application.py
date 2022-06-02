import inspect
from collections.abc import Coroutine
from types import ModuleType
from typing import Any

from asgikit.requests import HttpRequest
from asgikit.responses import HttpResponse, HTTPStatus
from asgikit.websockets import WebSocket

from selva.di import Container
from selva.di.decorators import DI_SERVICE_ATTRIBUTE
from selva.utils import package_scan
from selva.web.request import from_request
from selva.web.request.converter import FromRequest
from selva.web.routing import param_converter
from selva.web.routing.decorators import CONTROLLER_ATTRIBUTE
from selva.web.routing.router import Router


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
        self.di.scan(from_request, param_converter)

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http":
                await self._handle_request(HttpRequest(scope, receive, send))
            case "websocket":
                await self._handle_request(WebSocket(scope, receive, send))
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError()

    def controllers(self, *args: type):
        for controller in args:
            self.router.route(controller)

    def services(self, *args: type):
        for service in args:
            self.di.service(service)

    def modules(self, *modules: str | ModuleType):
        def is_controller(arg):
            return hasattr(arg, CONTROLLER_ATTRIBUTE)

        def is_service(arg):
            return hasattr(arg, DI_SERVICE_ATTRIBUTE)

        controllers = []
        services = []
        for item in package_scan.scan_packages(modules):
            if is_controller(item):
                controllers.append(item)
            if is_service(item):
                services.append(item)

        self.controllers(*controllers)
        self.services(*services)

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
                    await self.di.run_singleton_finalizers()
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as err:
                    await send(
                        {"type": "lifespan.shutdown.failed", "message": str(err)}
                    )
                break

    async def _get_params_from_request(
        self, request: HttpRequest | WebSocket, params: dict[str, type]
    ) -> dict[str, Any]:
        request_params = {}

        for name, item_type in params.items():
            converter = await self.di.get(FromRequest[item_type])
            value = await converter.from_request(request)
            request_params[name] = value

        return request_params

    async def _handle_request(
        self, request: HttpRequest | WebSocket
    ) -> Any | Coroutine:
        scope = request.scope
        receive, send = request.asgi

        method = request.method if request.is_http else None
        path = request.path

        match = self.router.match(method, path)

        if not match:
            response = HttpResponse(status=HTTPStatus.NOT_FOUND)
            await response(scope, receive, send)
            return

        controller = match.route.controller
        action = match.route.action
        path_params = match.params
        request_params = await self._get_params_from_request(
            request, match.route.request_params
        )

        all_params = path_params | request_params

        instance = await self.di.create(controller, context=request)

        try:
            response = action(instance, **all_params)

            if inspect.iscoroutine(response):
                response = await response

            if request.is_http:
                await response(scope, receive, send)
        except Exception as err:
            print(err)
            response = HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)
            await response(scope, receive, send)
