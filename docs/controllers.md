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
from selva.web import RequestContext, controller, get, websocket


@controller
class MyController:
    @get
    def handler(self, context: RequestContext):
        assert context.request is not None
        assert context.websocket is None
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
