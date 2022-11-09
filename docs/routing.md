# Routing

Routing is defined by the decorators in the controllers and handlers.

## Path parameters

Parameters can be defined in the handler's path using the syntax `:parameter_name`,
where `parameter_name` must be the name of the argument on the handler's signature.

```python
@controller
class Controller:
    @get("hello/:name")
    def handler(self, name: str):
        return f"Hello, {name}!"
```

## Path matching

The default behavior is for a path parameter to match a single path segment.
If you want to match the whole path, or a subpath of the request path,
use the syntax `*parameter_name`.

```python
@controller
class Controller:
    @get("hello/*path")
    def handler(self, path: str):
        name = " ".join(path.split("/"))
        return f"Hello, {name}!"
```

For a request like `GET hello/wonderful/Python/world`, the handler will output
`Hello, wonderful Python world!`.

You can mix both types of parameters with no problem:

- `*path`
- `*path/literal_segment`
- `:normal_param/*path`
- `:normal_param/*path/:other_path`

## Parameter conversion
Parameter conversion is done through the type annotation on the parameter. Selva
will try to find a converter suitable for the parameter type and then convert
the value before calling the handler method.

```python
@controller
class Controller:
    @get("repeat/:amount")
    def handler(self, amount: int):
        return {f"repeat {i}": i for i in range(amount)}
```

Selva already provide converters for the types `str`, `int`, `float` and `bool`.

## Custom parameter conversion

Conversion can be customized by providing an implementing of `selva.web.PathConverter[Type]`.

```python
from dataclasses import dataclass
from selva.di import service
from selva.web import PathConverter, controller, get


@dataclass
class MyModel:
    name: str


@service(provides=PathConverter[MyModel])
class MyModelPathConverter:
    def from_path(self, value: str) -> MyModel:
        return MyModel(value)


@controller
class MyController:
    @get("/:model")
    def handler(self, model: MyModel):
        return str(model)
```

If the `PathConverter` implementation raise an error, the handler is not called.
And if the error is a subclass of `selva.web.errors.HttpError`, for example
`UnathorizedError`, a response will be returned according to the error.

The `PathConverter` can also be provided a method called `:::python into_path(self, obj) -> str`
that is used to convert the object back into the path. This is used to build urls
from routes. If not implemented, the default calls `str` on the object.
