# Routing

Routing is defined by the decorators in the controllers and handlers.

## Path parameters

Parameters can be defined in the handler's path using the syntax `:::python "{parameter_name}"`,
where `parameter_name` must be the name of the argument on the handler's signature.

```python
@controller
class Controller:
    @get("hello/{name}")
    def handler(self, name: str):
        return f"Hello, {name}"
```

## Parameter conversion
Parameter conversion is done through the type annotation on the parameter. Selva
will try to find a converter suitable for the parameter type and then convert
the value before calling the handler method.

```python
@controller
class Controller:
    @get("repeat/{amount}")
    def handler(self, amount: int):
        return {f"repeat {i}": i for i in range(amount)}
```

Selva already provide converters for the types `str`, `int`, `float` and `bool`.

## Custom parameter conversion

Conversion can be customized by decorating a class with `:::python @path_param_converter`,
which must implement the following methods

* `:::python from_path(value: str) -> T`
* `:::python to_path(obj: T) -> str`:

The method `to_path` is used to build url for routes.

```python
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
    @get("{model}")
    def handler(self, model: MyModel):
        return str(model)
```
