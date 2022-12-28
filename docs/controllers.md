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
from selva.di import service, Inject
from selva.web import controller


@service
class MyService:
    pass


@controller
class MyController:
    my_service: MyService = Inject()
```

## Request Information

Handler methods can receive a parameter annotated with type `RequestContext`
that provides access to request information (path, method, headers, query
string, request body). The underlying http request or websocket from
[starlette](https://www.starlette.io/) can be accessed via  the properties
`RequestContext.request` or `RequestContext.websocket`, respectively.

`RequestContext` provides the following methods:

```python
def is_http() -> bool
def is_websocket() -> bool
def method() -> HTTPMethod | None
def url() -> URL
def base_url() -> URL
def path() -> str
def headers() -> Headers
def query() -> QueryParams
def cookies() -> Mapping[str, str]
def client() -> Address | None
```

!!! attention

    For http requests, `RequestContext.websocket` will be `None`, and for
    websocket requests, `RequestContext.request` will be `None`

```python
from selva.web import RequestContext, controller, get, websocket
from selva.web.request import HTTPMethod


@controller
class MyController:
    @get
    def handler(self, context: RequestContext):
        assert context.request is not None
        assert context.websocket is None

        assert context.method == HTTPMethod.GET
        assert context.path == "/"
        return context.path

    @websocket
    async def ws_handler(self, context: RequestContext):
        assert context.request is None
        assert context.websocket is not None
        
        ws = context.websocket
        await ws.accept()
        while True:
            data = await ws.receive()
            await ws.send_text(data)
```

## Request body

There are several methods to access the request body:

```python
async def stream() -> AsyncIterable[bytes]
async def body() -> bytes
async def json() -> dict | list
async def form() -> dict
```

## Websockets

For websocket, there are the following methods:

```python
async def accept(subprotocol: str = None, headers: Iterable[tuple[bytes, bytes]] = None)
async def receive() -> Message
async def send(message: Message) -> Awaitable
async def receive_text() -> str
async def receive_bytes() -> bytes
async def receive_json(mode: str = "text") -> Any
async def iter_text() -> str
async def iter_bytes() -> AsyncIterator[bytes]
async def iter_json() -> AsyncIterator[Any]
async def send_text(data: str)
async def send_bytes(data: bytes)
async def send_json(data: Any, mode: str = "text")
async def close(code: int = 1000, reason: str = None)
```

## Request Parameters

Handler methods can receive additional parameters, which will be extracted from
the request context using an implementation of `selva.web.FromRequest[Type]`.
If there is no direct implementation of `FromRequest[Type]`, Selva will iterate
over the base types of `Type` until an implementation is found or an error will
be returned if there is none.

```python
from selva.di import service
from selva.web import RequestContext, controller, get
from selva.web.converter import FromRequest


class Param:
    def __init__(self, path: str):
        self.request_path = path


@service(provides=FromRequest[Param])
class ParamFromRequest:
    def from_request(self, context: RequestContext) -> Param:
        return Param(context.path)


@controller
class MyController:
    @get
    def handler(self, param: Param):
        return param.request_path
```

If the `FromRequest` implementation raise an error, the handler is not called.
And if the error is a subclass of `selva.web.error.HTTPError`, for example
`UnathorizedError`, a response will be returned according to the error.

```python
from selva.di import service
from selva.web import RequestContext
from selva.web.converter import FromRequest
from selva.web.error import HTTPUnauthorizedError


@service(provides=FromRequest[Param])
class ParamFromRequest:
    def from_request(self, context: RequestContext) -> Param:
        if "authorization" not in context.headers:
            raise HTTPUnauthorizedError()
        return Param(context.path)
```

## Responses

Handler methods can return an instance of `selva.web.response.Response`, which
provides shortcut methods for several response types.

```python
from selva.web import controller, get
from selva.web.response import PlainTextResponse


@controller
class Controller:
    @get
    def handler(self) -> PlainTextResponse:
        return PlainTextResponse("Ok")
```

Handler methods can also return objects that have a corresponding `selva.web.converter.IntoResponse[Type]`
implementation. As with `FromRequest[Type]`, Selva will iterate over the base
types of `Type` until an implementation is found or an error will be returned.

```python
from selva.di import service
from selva.web import controller, get
from selva.web.converter import IntoResponse
from selva.web.response import JSONResponse


class Result:
    def __init__(self, data: str):
        self.data = data


@service(provides=IntoResponse[Result])
class ResultIntoResponse:
    def into_response(self, value: Result) -> JSONResponse:
        return JSONResponse({"result": value.data})


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
- `os.PathLike` (file response)
