# Controllers

## Overview

Controllers are classes responsible for handling requests through handler methods.
They are defined using the `@controller` on the class and `@get`, `@post`, `@put`,
`@patch`, `@delete` and `@websocket` on each of the handler methods.

Handler methods must receive, at least, two parameters: `Request` and `Response`.
It is not needed to annotate the request and response parameters, but they should
be the first two parameters.

```python
from asgikit.requests import Request, read_json
from asgikit.responses import respond_text, respond_redirect
from selva.web import controller, get, post
import structlog

logger = structlog.get_logger()


@controller
class IndexController:
    @get
    async def index(self, request: Request):
        await respond_text(request.response, "application root")


@controller("admin")
class AdminController:
    @post("send")
    async def handle_data(self, request: Request):
        logger.info("request body", content=str(await read_json(request)))
        await respond_redirect(request.response, "/")
```

!!! note
    Defining a path on `@controller` or `@get @post etc...` is optional and
    defaults to an empty string `""`.

Handler methods can be defined with path parameters, which can be bound to the
handler with the annotation `FromPath`:

```python
from typing import Annotated
from selva.web import get, FromPath


@get("/:path_param")
def handler(request, path_param: Annotated[str, FromPath]):
    ...
```

It is also possible to explicitly declare from which parameter the value will
be retrieved from:

```python
@get("/:path_param")
def handler(req, res, value: Annotated[str, FromPath("path_param")]):
    ...
```


The [routing section](routing.md) provides more information about path parameters

## Dependencies

Controllers themselves are services, and therefore can have services injected.

```python
from typing import Annotated
from selva.di import service, Inject
from selva.web import controller


@service
class MyService:
    pass


@controller
class MyController:
    my_service: Annotated[MyService, Inject]
```

## Request Information

Handler methods receive an object of type `asgikit.requests.Request` as the first
parameter that provides access to request information (path, method, headers, query
string, request body). It also provides the `asgikit.responses.Response` or
`asgikit.websockets.WebSocket` objects to either respond the request or interact
with the client via websocket.

!!! attention

    For http requests, `Request.websocket` will be `None`, and for
    websocket requests, `Request.response` will be `None`

```python
from http import HTTPMethod, HTTPStatus
from asgikit.requests import Request
from asgikit.responses import respond_json
from selva.web import controller, get, websocket


@controller
class MyController:
    @get
    async def handler(self, request: Request):
        assert request.response is not None
        assert request.websocket is None

        assert request.method == HTTPMethod.GET
        assert request.path == "/"
        await respond_json(request.response, {"status": HTTPStatus.OK})

    @websocket
    async def ws_handler(self, request: Request):
        assert request.response is None
        assert request.websocket is not None
        
        ws = request.websocket
        await ws.accept()
        while True:
            data = await ws.receive()
            await ws.send(data)
```

## Request body

`asgikit` provides several functions to retrieve the request body:

```python
async def read_body(request: Request) -> bytes
async def read_text(request: Request, encoding: str = None) -> str
async def read_json(request: Request) -> dict | list
async def read_form(request: Request) -> dict[str, str | multipart.File]:
```

## Websockets

For websocket, there are the following methods:

```python
async def accept(subprotocol: str = None, headers: Iterable[tuple[bytes, bytes]] = None)
async def receive(self) -> str | bytes
async def send(self, data: bytes | str)
async def close(self, code: int = 1000, reason: str = "")
```

## Request Parameters

Handler methods can receive additional parameters, which will be extracted from
the request using an implementation of `selva.web.FromRequest[Type]`.
If there is no direct implementation of `FromRequest[Type]`, Selva will iterate
over the base types of `Type` until an implementation is found or an error will
be returned if there is none.

You can use the `register_from_request` decorator to register an `FromRequest` implementation.

```python
from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import controller, get
from selva.web.converter.decorator import register_from_request


class Param:
    def __init__(self, path: str):
        self.request_path = path


@register_from_request(Param)
class ParamFromRequest:
    def from_request(
        self,
        request: Request,
        original_type,
        parameter_name,
        metadata = None,
    ) -> Param:
        return Param(request.path)


@controller
class MyController:
    @get
    async def handler(self, request: Request, param: Param):
        await respond_text(request.response, param.request_path)
```

If the `FromRequest` implementation raise an error, the handler is not called.
And if the error is a subclass of `selva.web.error.HTTPError`, for instance
`UnathorizedError`, a response will be produced according to the error.

```python
from selva.web.exception import HTTPUnauthorizedException


@register_from_request(Param)
class ParamFromRequest:
    def from_request(
        self,
        request: Request,
        original_type,
        parameter_name,
        metadata = None,
    ) -> Param:
        if "authorization" not in request.headers:
            raise HTTPUnauthorizedException()
        return Param(context.path)
```

### Pydantic

Selva already implements `FromRequest[pydantic.BaseModel]` by reading the request
body and parsing the input into the pydantic model, if the content type is json
or form, otherwise raising an `HTTPError` with status code 415. It is also implemented
for `list[pydantic.BaseModel]`.

## Responses

Inheriting the `asgikit.responses.Response` from `asgikit`, the handler methods
do not return a response, instead they write to the response.

```python
from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import controller, get


@controller
class Controller:
    @get
    async def handler(self, request: Request):
        await respond_text(request.response, "Ok")
```
