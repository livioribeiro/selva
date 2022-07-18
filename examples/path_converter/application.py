from dataclasses import dataclass

from selva.web import controller, get, PathConverter


@dataclass
class MyModel:
    name: str


class MyModelPathParamConverter(PathConverter[MyModel]):
    def from_path(self, value: str) -> MyModel:
        return MyModel(value)

    def into_path(self, obj: MyModel) -> str:
        return obj.name


@controller
class MyController:
    @get("/int/{param}")
    def handler_int(self, param: int):
        return str(param)

    @get("float/{param}")
    def handler_float(self, param: float):
        return str(param)

    @get("bool/{param}")
    def handler_bool(self, param: bool):
        return str(param)

    @get("/custom/{my_model}")
    def handler_custom(self, my_model: MyModel):
        return str(my_model)
