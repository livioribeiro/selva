# Controllers

## Overview

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

Handler methods can be defined with path parameters, which will be bound to the
handler's arguments with the same name:

```python
@get("/:path_param")
def handler(path_param):
    ...
```

The [routing section](../routing) provides more information about path parameters

## Dependencies

Controllers themselves are services, and therefore can have services injected.

```python
from selva.di import service
from selva.web import controller


@service
class MyService:
    pass


@controller
class MyController:
    def __init__(self, my_service: MyService):
        self.service = my_service
```

## Request Information

Handler methods can receive a parameter annotated with type `RequestContext`
that provides access to request information (path, method, headers, query
string, request body). The underlying http request or websocket from
[asgikit](https://pypi.org/project/asgikit/) can be accessed via  the properties
`RequestContext.request` or `RequestContext.websocket`, respectively.

!!! attention

    For http requests, `RequestContext.websocket` will be `None`, and for
    websocket requests, `RequestContext.request` will be `None`

`RequestContext` uses `__getattr__` to proxy methods from the underlying `HttpRequest` or `WebSocket`

```python
from selva.web import HttpMethod, RequestContext, controller, get, websocket


@controller
class MyController:
    @get
    def handler(self, context: RequestContext):
        assert context.request is not None
        assert context.websocket is None
        assert context.method == HttpMethod.GET
        assert context.path == "/"
        return context.path

    @websocket
    async def ws_handler(self, context: RequestContext):
        assert context.request is None
        assert context.websocket is not None
        await context.accept()
        while True:
            data = await context.receive()
            await context.send_text(data)
```

## Request body

There are several methods to access the request body:

```python
async def stream() -> AsyncIterable[bytes]
async def body() -> bytes
async def text() -> str
async def json() -> dict | list
async def form() -> dict
```

## Websockets

For websocket, `RequestContext` will have following methods:

```python
async def accept()
async def receive() -> str | bytes
async def send_text(data: str)
async def send_bytes(data: bytes)
async def send_json(data: dict)
async def close(code: int = None)
```

## Request Parameters

Handler methods can receive additional parameters, which will be extracted from
the request context using an implementation of `selva.web.FromRequest[Type]`.
If there is no direct implementation of `FromRequest[Type]`, Selva will iterate
over the base types of `Type` until an implementation is found or an error will
be returned if there is none.

```python
from selva.web import RequestContext, FromRequest, controller, get


class Param:
    def __init__(self, path: str):
        self.request_path = path


class ParamFromRequest(FromRequest[Param]):
    def from_request(self, context: RequestContext) -> Param:
        return Param(context.path)


@controller
class MyController:
    @get
    def handler(self, param: Param):
        return param.request_path
```

If the `FromRequest` implementation raise an error, the handler is not called.
And if the error is a subclass of `selva.web.errors.HttpError`, for example
`UnathorizedError`, a response will be returned according to the error.

```python
from selva.web.errors import UnauthorizedError


class ParamFromRequest(FromRequest[Param]):
    def from_request(self, context: RequestContext) -> Param:
        if "authorization" not in context.headers:
            raise UnauthorizedError()
        return Param(context.path)
```

## Responses

Handler methods can return an instance of `selva.web.HttpResponse`, which
provides shortcut methods for several response types.

```python
from selva.web import HttpResponse, controller, get


@controller
class Controller:
    @get
    def handler(self) -> HttpResponse:
        return HttpResponse.text("Ok")
```

Handler methods can also return objects that have a corresponding `selva.web.IntoResponse[Type]`
implementation. As with `FromRequest[Type]`, Selva will iterate over the base
types of `Type` until an implementation is found or an error will be returned.

```python
from selva.web import HttpResponse, IntoResponse, controller, get


class Result:
    def __init__(self, data: str):
        self.data = data


class ResultIntoResponse(IntoResponse[Result]):
    def into_response(self, value: Result) -> HttpResponse:
        return HttpResponse.json({"result": value.data})


@controller
class MyController:
    @get
    def handler(self) -> Result:
        return Result("OK")
```

There are already implementations of `IntoResponse` for the following:

- `int` (response with status code)
- [`http.HTTPStatus`](https://docs.python.org/3/library/http.html#http.HTTPStatus) (response with status code)
- `str` (text response)
- `list` (json response)
- `dict` (json response)
- `set` (json response)
