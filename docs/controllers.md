# Controllers

Controllers are classes responsible for handling requests through handler methods.
They are defined using the `@controller` on the class and `@get`, `@post`, `@put`,
`@patch`, `@delete` and `@websocket` on each of the handler methods.

```python
from selva.web import HttpResponse, RequestContext, controller, get, post


@controller
class IndexController:
    @get
    def index(self):
        return "application root"


@controller("admin")
class AdminController:
    @post("send")
    async def handle_data(self, context: RequestContext):
        print(await context.request.json())
        return HttpResponse.redirect("/")
```

!!! note
    Defining a path on `@controller` or `@get @post etc...` is optional and
    defaults to an empty string `""`.

## Path parameters

Parameters can be defined in the handler's path:

```python
@controller
class Controller:
    @get("hello/{name}")
    def handler(self, name: str):
        return f"Hello, {name}"
```

Parameter conversion is done by the type annotation on the parameter:

```python
@controller
class Controller:
    @get("repeat/{amount}")
    def handler(self, amount: int):
        return {f"repeat {i}": i for i in range(amount)}
```

Conversion can be customized by decorating a class with `path_param_converter`,
which must have the methods `from_path(value: str) -> T` and `to_path(obj: T) -> str`:

```python
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
    @get("{model}")
    def handler(self, model: MyModel):
        return str(model)
```

## Request Information

Handler methods can receive a parameter annotated with type `RequestContext`
that provides access to request information (path, method, headers, query
string, request  body). There are several methods to access the request body:

* `async def stream() -> AsyncIterable[bytes]`
* `async def body() -> bytes`
* `async def text() -> str`
* `async def json() -> dict | list`
* `async def form() -> dict`

For websocket, the `RequestContext` will have other methods available:

* `async def accept()`
* `async def receive() -> str | bytes`
* `async def send_text(data: str)`
* `async def send_bytes(data: bytes)`
* `async def send_json(data: dict)`
* `async def close(code: int = None)`
