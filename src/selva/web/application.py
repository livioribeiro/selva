import inspect
from collections.abc import Iterable
from types import ModuleType
from typing import Any

from asgikit.requests import HttpRequest
from asgikit.responses import HttpResponse, HTTPStatus
from asgikit.websockets import WebSocket

from selva.di import Container

from .routing.decorators import CONTROLLER_ATTRIBUTE
from .routing.router import Router


class Application:
    def __init__(
        self,
        *,
        debug=False,
    ):
        self.debug = debug
        self.__di_container = Container()
        self.__router = Router()

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

        return self

    def modules(self, *args: ModuleType):
        def predicate(arg):
            return isinstance(arg, type) and hasattr(arg, CONTROLLER_ATTRIBUTE)

        for module in args:
            self.controllers(
                *map(lambda member: member[1], inspect.getmembers(module, predicate))
            )

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

    async def _handle_http(self, scope, receive, send):
        request = HttpRequest(scope, receive, send)
        self.attach_to_request_context(HttpRequest, request, request)
        match = self.__router.match_http(request)

        if not match:
            response = HttpResponse(status=HTTPStatus.NOT_FOUND)
            await response(scope, receive, send)
            return

        controller = match.route.controller
        action = match.route.action
        params = match.params

        instance = await self.__di_container.create(controller, context=request)
        result = action(instance, **params)
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

        instance = await self.__di_container.create(controller, context=websocket)

        await action(instance, websocket, **params)
