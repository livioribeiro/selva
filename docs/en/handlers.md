# Handlers

## Overview

Handlers are functions responsible for handling received requests.
They are defined using the `@get`, `@post`, `@put`, `@patch`, `@delete` and `@websocket`
decorators.

Handlers must receive, at least, the request object as the first parameter.
It is not needed to annotate the request parameter, but it should be the first parameter.

```python
from asgikit.requests import Request, read_json
from asgikit.responses import respond_text, respond_redirect
from selva.web import get, post
import structlog

logger = structlog.get_logger()


@get
async def index(request: Request):
    await respond_text(request.response, "application root")


@post("send")
async def handle_data(request: Request):
    content = await read_json(request)
    logger.info("request body", content=repr(content))
    await respond_redirect(request.response, "/")
```

!!! note
    Defining a path on `@get @post etc...` is optional and defaults to an empty string `""`.

Handler function can be defined with path parameters, which can be bound to the
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
from typing import Annotated
from selva.web import get, FromPath


@get("/:path_param")
def handler(request, value: Annotated[str, FromPath("path_param")]):
    ...
```

The [routing section](routing.md) provides more information about path parameters

## Responses

Inheriting the `asgikit.responses.Response` from `asgikit`, the handler functions
do not return a response, instead they write to the response.

```python
from asgikit.requests import Request
from asgikit.responses import respond_json
from selva.web import get


@get
async def handler(request: Request):
    await respond_json(request.response, {"data": "The response"})
```

`asgikit` provides function to write data to the response:

```python
from collections.abc import AsyncIterable
from http import HTTPStatus

from asgikit.responses import Response


async def respond_text(response: Response, content: str | bytes): ...
async def respond_status(response: Response, status: HTTPStatus): ...
async def respond_redirect(response: Response, location: str, permanent: bool = False): ...
async def respond_redirect_post_get(response: Response, location: str): ...
async def respond_json(response: Response, content): ...
async def stream_writer(response: Response): ...
async def respond_stream(response: Response, stream: AsyncIterable[bytes | str]): ...
```

## Dependencies

Handler functions can receive services as parameters that will be injected when the handler is called.

```python
from typing import Annotated
from selva.di import service, Inject
from selva.web import get


@service
class MyService:
    pass


@get
def my_handler(request, my_service: Annotated[MyService, Inject]):
    ...
```

## Request Information

Handler functions receive an object of type `asgikit.requests.Request` as the first
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
from selva.web import get, websocket


@get
async def handler(request: Request):
    assert request.response is not None
    assert request.websocket is None

    assert request.method == HTTPMethod.GET
    assert request.path == "/"
    await respond_json(request.response, {"status": HTTPStatus.OK})

@websocket
async def ws_handler(request: Request):
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
from asgikit.requests import Body, Request
from python_multipart import multipart


async def read_body(request: Body | Request) -> bytes: ...
async def read_text(request: Body | Request, encoding: str = None) -> str: ...
async def read_json(request: Body | Request) -> dict | list: ...
async def read_form(request: Body | Request) -> dict[str, str | multipart.File]: ...
```

## Websockets

For websockets, there are the following functions:

```python
from collections.abc import Iterable


async def accept(subprotocol: str = None, headers: Iterable[tuple[str, str | list[str]]] = None): ...
async def receive(self) -> str | bytes: ...
async def send(self, data: bytes | str): ...
async def close(self, code: int = 1000, reason: str = ""): ...
```

## Request Parameters

Handler functions can receive additional parameters, which will be extracted from
the request using an implementation of `selva.web.FromRequest[T]`.
If there is no direct implementation of `FromRequest[T]`, Selva will iterate
over the base types of `T` until an implementation is found or an error will
be returned if there is none.

You can use the `register_from_request` decorator to register an `FromRequest` implementation.

```python
from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import get
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
        metadata,
        optional,
    ) -> Param:
        return Param(request.path)


@get
async def handler(request: Request, param: Param):
    await respond_text(request.response, param.request_path)
```

If the `FromRequest` implementation raise an error, the handler is not called.
And if the error is a subclass of `selva.web.error.HTTPError`, for instance
`HTTPUnauthorizedException`, a response will be produced according to the error.

```python
from selva.web.exception import HTTPUnauthorizedException


@register_from_request(Param)
class ParamFromRequest:
    def from_request(
        self,
        request: Request,
        original_type,
        parameter_name,
        metadata,
        optional,
    ) -> Param:
        if "authorization" not in request.headers:
            raise HTTPUnauthorizedException()
        return Param(context.path)
```

### Annotated parameters

If the parameter is annotated (`Annotated[T, U]`) the framework will look for an
implementation of `FromRequest[U]`, with `T` being passed as the `original_type`
parameter and `U` as the `metadata` parameter.

### Pydantic

Selva already implements `FromRequest[pydantic.BaseModel]` by reading the request
body and parsing the input into the pydantic model, if the content type is json
or form, otherwise raising an `HTTPError` with status code 415. It is also implemented
for `list[pydantic.BaseModel]`.
