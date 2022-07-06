from dataclasses import dataclass

from selva.web import controller, get
from selva.web.routing.converter import path_param_converter


@dataclass
class MyModel:
    name: str


@path_param_converter(MyModel)
class MyModelPathParamConverter:
    async def from_path(self, value: str) -> MyModel:
        return MyModel(value)

    async def to_path(self, obj: MyModel) -> str:
        return obj.name


@controller
class MyController:
    @get("{my_model}")
    def handler(self, my_model: MyModel):
        return str(my_model)
