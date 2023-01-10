from dataclasses import dataclass
from pathlib import PurePath

from selva.di import service
from selva.web import PathParamConverter, controller, get


@dataclass
class MyModel:
    name: str


@service(provides=PathParamConverter[MyModel])
class MyModelPathParamConverter:
    def from_path(self, value: str) -> MyModel:
        return MyModel(value)

    def into_path(self, obj: MyModel) -> str:
        return obj.name


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

    @get("/custom/:my_model")
    def handler_custom(self, my_model: MyModel):
        return str(my_model)

    @get("/path/*path")
    def handler_path(self, path: PurePath):
        return path.as_posix()
