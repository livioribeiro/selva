from dataclasses import dataclass
from pathlib import PurePath
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_text

from selva.web import FromPath, FromQuery, controller, get
from selva.web.converter.decorator import register_param_converter


@dataclass
class MyModel:
    name: str


@register_param_converter(MyModel)
class MyModelParamConverter:
    def from_str(self, value: str) -> MyModel:
        return MyModel(value)


@controller
class MyController:
    @get("/int/:param")
    async def handler_int(self, request: Request, param: Annotated[int, FromPath]):
        await respond_text(request.response, str(param))

    @get("/float/:param")
    async def handler_float(self, request: Request, param: Annotated[float, FromPath]):
        await respond_text(request.response, str(param))

    @get("/bool/:param")
    async def handler_bool(self, request: Request, param: Annotated[bool, FromPath]):
        await respond_text(request.response, str(param))

    @get("/custom/")
    async def handler_custom_query(
        self, request: Request, param: Annotated[MyModel, FromQuery]
    ):
        await respond_text(request.response, str(param))

    @get("/custom/:param")
    async def handler_custom(
        self, request: Request, param: Annotated[MyModel, FromPath]
    ):
        await respond_text(request.response, str(param))

    @get("/path/*path")
    async def handler_path(self, request: Request, path: Annotated[PurePath, FromPath]):
        await respond_text(request.response, str(path))
