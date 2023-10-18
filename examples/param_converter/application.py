from dataclasses import dataclass
from typing import Annotated
from pathlib import PurePath

from asgikit.requests import Request
from asgikit.responses import Response, respond_text

from selva.di import service
from selva.web import controller, get, FromQuery
from selva.web.converter import ParamConverter


@dataclass
class MyModel:
    name: str


@service(provides=ParamConverter[MyModel])
class MyModelParamConverter:
    def from_param(self, value: str) -> MyModel:
        return MyModel(value)


@controller
class MyController:
    @get("/int/:param")
    async def handler_int(self, req: Request, res: Response, param: int):
        await respond_text(res, str(param))

    @get("/float/:param")
    async def handler_float(self, req: Request, res: Response, param: float):
        await respond_text(res, str(param))

    @get("/bool/:param")
    async def handler_bool(self, req: Request, res: Response, param: bool):
        await respond_text(res, str(param))

    @get("/custom/")
    async def handler_custom_query(self, req: Request, res: Response, param: Annotated[MyModel, FromQuery]):
        await respond_text(res, str(param))

    @get("/custom/:param")
    async def handler_custom(self, req: Request, res: Response, param: MyModel):
        await respond_text(res, str(param))

    @get("/path/*path")
    async def handler_path(self, req: Request, res: Response, path: PurePath):
        await respond_text(res, str(path))
