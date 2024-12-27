from dataclasses import dataclass
from pathlib import PurePath
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_text

from selva.di import service
from selva.web import FromPath, FromQuery, get
from selva.web.converter.param_converter import ParamConverter


@dataclass
class MyModel:
    name: str


@service
async def my_model_param_converter(locator) -> ParamConverter[MyModel]:
    return MyModelParamConverter()


class MyModelParamConverter:
    def from_str(self, value: str) -> MyModel:
        return MyModel(value)

    def into_str(self, data: MyModel) -> str:
        return str(data)


@get("/int/:param")
async def handler_int(request: Request, param: Annotated[int, FromPath]):
    await respond_text(request.response, str(param))


@get("/float/:param")
async def handler_float(request: Request, param: Annotated[float, FromPath]):
    await respond_text(request.response, str(param))


@get("/bool/:param")
async def handler_bool(request: Request, param: Annotated[bool, FromPath]):
    await respond_text(request.response, str(param))


@get("/custom/")
async def handler_custom_query(
    request: Request, param: Annotated[MyModel, FromQuery]
):
    await respond_text(request.response, str(param))


@get("/custom/:param")
async def handler_custom(
    request: Request, param: Annotated[MyModel, FromPath]
):
    await respond_text(request.response, str(param))


@get("/path/*path")
async def handler_path(request: Request, path: Annotated[PurePath, FromPath]):
    await respond_text(request.response, str(path))
