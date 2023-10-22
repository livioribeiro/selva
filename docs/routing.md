# Routing

Routing is defined by the decorators in the controllers and handlers.

## Path parameters

Parameters can be defined in the handler's path using the syntax `:parameter_name`,
where `parameter_name` must be the name of the argument on the handler's signature.

```python
from typing import Annotated
from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import controller, get, FromPath


@controller
class Controller:
    @get("hello/:name")
    async def handler(self, request: Request, name: Annotated[str, FromPath]):
        await respond_text(request.response, f"Hello, {name}!")
```

Here was used `Annotated` and `FromPath` to indicated that the handler argument
is to be bound to the parameter from the request path. More on that will be explained
in the following sections.

## Path matching

The default behavior is for a path parameter to match a single path segment.
If you want to match the whole path, or a subpath of the request path,
use the syntax `*parameter_name`.

```python
from typing import Annotated
from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import controller, get, FromPath


@controller
class Controller:
    @get("hello/*path")
    async def handler(self, request: Request, path: Annotated[str, FromPath]):
        name = " ".join(path.split("/"))
        await respond_text(request.response, f"Hello, {name}!")
```

For a request like `GET hello/Python/World`, the handler will output
`Hello, Python World!`.

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
from typing import Annotated
from asgikit.requests import Request
from asgikit.responses import respond_json
from selva.web import controller, get, FromPath


@controller
class Controller:
    @get("repeat/:amount")
    async def handler(self, request: Request, amount: Annotated[int, FromPath]):
        await respond_json(request.response, {f"repeat {i}": i for i in range(amount)})
```

The type annotation indicates that we want a value of type `int` that should be
taken from the request path.

Selva already provide converters for the types `str`, `int`, `float`, `bool` and `pathlib.PurePath`.

## Custom parameter conversion

Conversion can be customized by providing an implementing of `selva.web.converter.param_converter.ParamConverter`.
You normally use the shortcut decorator `selva.web.converter.decodator.register_param_converter.`

```python
from dataclasses import dataclass
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import controller, get, FromPath
from selva.web.converter.decorator import register_param_converter


@dataclass
class MyModel:
    name: str


@register_param_converter(MyModel)
class MyModelParamConverter:
    def from_str(self, value: str) -> MyModel:
        return MyModel(value)


@controller
class MyController:
    @get("/:model")
    async def handler(self, request: Request, model: Annotated[MyModel, FromPath]):
        await respond_text(request.response, str(model))
```

If the `ParamConverter` implementation raise an error, the handler is not called.
And if the error is a subclass of `selva.web.error.HTTPError`, for instance
`UnathorizedError`, a response will be produced according to the error.

The `ParamConverter` can also be provided a method called `:::python into_str(self, obj) -> str`
that is used to convert the object back. This is used to build urls from routes.
If not implemented, the default calls `str` on the object.
