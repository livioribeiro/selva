import inspect
from types import ModuleType
from typing import Any

from asgikit.requests import HttpRequest
from asgikit.responses import HttpResponse, HTTPStatus
from asgikit.websockets import WebSocket

from selva.di import Container
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
        self.__di_container = Container()
        self.__router = Router()
        self.__di_container.scan(from_request, param_converter)

    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            await self.handle_lifespan(scope, receive, send)
        elif scope["type"] == "http":
            await self._handle_http(scope, receive, send)
        elif scope["type"] == "websocket":
            await self._handle_websocket(scope, receive, send)
        else:
            raise RuntimeError()

    def controllers(self, *args: type):
        for controller in args:
            self.__router.route(controller)
            self.__di_container.register_transient(controller)

        return self

    def modules(self, *args: ModuleType):
        def predicate(arg):
            return isinstance(arg, type) and hasattr(arg, CONTROLLER_ATTRIBUTE)

        for module in args:
            controllers_classes = package_scan.scan_packages([module], predicate)
            self.controllers(*controllers_classes)

        return self

    def attach_to_request_context(
        self, target_type: type, target: Any, request: HttpRequest
    ):
        self.__di_container.define_dependent(target_type, target, context=request)

    async def handle_lifespan(self, _scope, receive, send):
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
                    await send({"type": "lifespan.startup.complete"})
                except Exception as err:
                    await send({"type": "lifespan.startup.failed", "message": str(err)})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                break

    async def from_request(
        self, request: HttpRequest | WebSocket, params: dict[str, type]
    ) -> dict[str, Any]:
        request_params = {}

        for name, item_type in params.items():
            converter = await self.__di_container.get(FromRequest[item_type])
            value = await converter.from_request(request)
            request_params[name] = value

        return request_params

    async def _handle_http(self, scope, receive, send):
        request = HttpRequest(scope, receive, send)
        match = self.__router.match_http(request)

        if not match:
            response = HttpResponse(status=HTTPStatus.NOT_FOUND)
            await response(scope, receive, send)
            return

        controller = match.route.controller
        action = match.route.action
        params = match.params

        request_params = await self.from_request(request, match.route.request_params)

        instance = await self.__di_container.create(controller, context=request)
        result = action(instance, **(params | request_params))
        response = await result if inspect.iscoroutine(result) else result

        await response(scope, receive, send)
        del request

    async def _handle_websocket(self, scope, receive, send):
        websocket = WebSocket(scope, receive, send)
        match = self.__router.match_websocket(websocket)

        if not match:
            response = HttpResponse(status=HTTPStatus.NOT_FOUND)
            await response(scope, receive, send)
            return

        controller = match.route.controller
        action = match.route.action
        params = match.params

        request_params = await self.from_request(websocket, match.route.request_params)

        instance = await self.__di_container.create(controller, context=websocket)

        await action(instance, **(params | request_params))
