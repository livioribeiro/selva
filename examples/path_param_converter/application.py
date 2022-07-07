from dataclasses import dataclass

from selva.web import controller, get, path_param_converter


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
    @get("/int/{param}")
    def handler_int(self, param: int):
        return str(param)

    @get("/custom/{my_model}")
    def handler_custom(self, my_model: MyModel):
        return str(my_model)
