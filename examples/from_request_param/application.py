from dataclasses import dataclass
from typing import Annotated
from pathlib import PurePath

from selva.di import service
from selva.web import controller, get, FromQuery
from selva.web.converter import FromRequestParam


@dataclass
class MyModel:
    name: str


@service(provides=FromRequestParam[MyModel])
class MyModelFromRequestParam:
    def from_param(self, value: str) -> MyModel:
        return MyModel(value)


@controller
class MyController:
    @get("/int/:param")
    def handler_int(self, param: int):
        return str(param)

    @get("/float/:param")
    def handler_float(self, param: float):
        return str(param)

    @get("/bool/:param")
    def handler_bool(self, param: bool):
        return str(param)

    @get("/custom/")
    def handler_custom_query(self, my_model: Annotated[MyModel, FromQuery]):
        return str(my_model)

    @get("/custom/:my_model")
    def handler_custom(self, my_model: MyModel):
        return str(my_model)

    @get("/path/*path")
    def handler_path(self, path: PurePath):
        return path.as_posix()
