from dataclasses import dataclass
from decimal import Decimal
from pathlib import PurePath
from typing import Annotated as A

from asgikit.requests import Request
from asgikit.responses import respond_text

from selva.web import FromPath, FromQuery, get
from selva.web.converter.decorator import register_converter


@dataclass
class MyModel:
    name: str


@register_converter(str, MyModel)
class MyModelParamConverter:
    def convert(self, value: str, original_type: type[MyModel]) -> MyModel:
        return MyModel(value)


@get("/int/:param")
async def handler_int(request: Request, param: A[int, FromPath]):
    await respond_text(request.response, str(param))


@get("/float/:param")
async def handler_float(request: Request, param: A[float, FromPath]):
    await respond_text(request.response, str(param))


@get("/decimal/:param")
async def handler_decimal(request: Request, param: A[Decimal, FromPath]):
    await respond_text(request.response, str(param))


@get("/bool/:param")
async def handler_bool(request: Request, param: A[bool, FromPath]):
    await respond_text(request.response, str(param))


@get("/custom/")
async def handler_custom_query(request: Request, param: A[MyModel, FromQuery]):
    await respond_text(request.response, str(param))


@get("/custom/:param")
async def handler_custom(request: Request, param: A[MyModel, FromPath]):
    await respond_text(request.response, str(param))


@get("/path/*path")
async def handler_path(request: Request, path: A[PurePath, FromPath]):
    await respond_text(request.response, str(path))
