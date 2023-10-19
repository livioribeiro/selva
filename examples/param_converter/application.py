from dataclasses import dataclass
from pathlib import PurePath
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import Response, respond_text

from selva.web import FromQuery, controller, get
from selva.web.converter import FromPath
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
    async def handler_int(
        self, req: Request, res: Response, param: Annotated[int, FromPath]
    ):
        await respond_text(res, str(param))

    @get("/float/:param")
    async def handler_float(
        self, req: Request, res: Response, param: Annotated[float, FromPath]
    ):
        await respond_text(res, str(param))

    @get("/bool/:param")
    async def handler_bool(
        self, req: Request, res: Response, param: Annotated[bool, FromPath]
    ):
        await respond_text(res, str(param))

    @get("/custom/")
    async def handler_custom_query(
        self, req: Request, res: Response, param: Annotated[MyModel, FromQuery]
    ):
        await respond_text(res, str(param))

    @get("/custom/:param")
    async def handler_custom(
        self, req: Request, res: Response, param: Annotated[MyModel, FromPath]
    ):
        await respond_text(res, str(param))

    @get("/path/*path")
    async def handler_path(
        self, req: Request, res: Response, path: Annotated[PurePath, FromPath]
    ):
        await respond_text(res, str(path))
