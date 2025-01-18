# Handlers

## Visão geral

Handlers são funções responsáveis por tratar as requisições recebidas.
Eles são definidos com os decoradores `@get`, `@post`, `@put`, `@patch`, `@delete`
and `@websocket`.

Handlers devem receber, pelo menos, o objeto da requisição como primeiro parâmetro.
Não é necessário anotar o parêmetro, mas ele deve ser o primeiro.

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
    Definir um caminho em `@get @post etc...` é opcional e tem valor padrão de string vazia `""`.

Handlers podem ser definidas com parâmetros de caminho, que serão ligadas
ao handler com a anotação `FromPath`:

```python
from typing import Annotated
from selva.web import get, FromPath


@get("/:path_param")
def handler(request, path_param: Annotated[str, FromPath]):
    ...
```

Também é possível declarar explicitamente de qual parâmetro o valor será recuperado:

```python
from typing import Annotated
from selva.web import get, FromPath


@get("/:path_param")
def handler(request, value: Annotated[str, FromPath("path_param")]):
    ...
```

A [seção de roteamento](routing.md) provê mais informações sobre parâmetros de caminho.

## Respostas

Herdando o `asgikit.responses.Response` de `asgikit`, os handlers não
retornam uma resposta, ao invés disso elas escrevem os dados na resposta.

```python
from asgikit.requests import Request
from asgikit.responses import respond_json
from selva.web import get


@get
async def handler(request: Request):
    await respond_json(request.response, {"data": "The response"})
```

`asgikit` provê funções para escrever dados na resposta:

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

## Dependências

Handlers podem receber serviços como parâmetros que serão injetados quando
o handler é chamado:

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

## Informações da requisição

Handlers recebem um objeto do tipo `asgikit.requests.Request` como primeiro
parâmetro que provê acesso às informações da requisição (caminho, método, cabeçalhos,
query string, corpo da requisição). Ele também provê o objeto `asgikit.responses.Response`
ou `asgikit.websockets.WebSocket` para responder à requisição ou interagir com o
cliente através do websocket.

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

## Corpo da requisição

`asgikit` provê várias funções para recuperar o corpo da requisição:

```python
from asgikit.requests import Body, Request
from python_multipart import multipart


async def read_body(request: Body | Request) -> bytes: ...
async def read_text(request: Body | Request, encoding: str = None) -> str: ...
async def read_json(request: Body | Request) -> dict | list: ...
async def read_form(request: Body | Request) -> dict[str, str | multipart.File]: ...
```

## Websockets

Para websockets, há as seguintes funções:

```python
from collections.abc import Iterable


async def accept(subprotocol: str = None, headers: Iterable[tuple[str, str | list[str]]] = None): ...
async def receive(self) -> str | bytes: ...
async def send(self, data: bytes | str): ...
async def close(self, code: int = 1000, reason: str = ""): ...
```

## Parâmetros da requisição

Handlers podem receber parâmetros adicionais, os quais serão extraídos
da requisição utilizando uma implementação de `selva.web.FromRequest[T]`.
Se n5ão houver uma implementação direta de `FromRequest[T]`, Selva procurará nos
tipos base de `T` até que uma implementação seja encontrada ou um erro será retornado.

Você pode usar o decorador `register_from_request` para registrar uma implementação
de `FromRequest`.

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

Se a implementação de `FromRequest` lançar um erro, o handler não é chamado.
E se o erro for uma subclassse de `selva.web.error.HTTPError`, por exemplo `HTTPUnauthorizedException`,
uma resposta será produzida de acordo como o erro.

```python
# ...
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

### Parâmetros anotados

Se o parâmetro for anotado (`Annotated[T, U]`) o framework procurará for uma implementação
de `FromRequest[U]`, com `T` sendo passado como o parâmetro `original_type` e `U`
como o parâmetro `metadata`.

### Pydantic

Selva já implementa `FromRequest[pydantic.BaseModel]` lendo o corpo da requisição
e carregando os dados no modelo pydantic, se o tipo de conteúdo for json ou formulário,
caso contrário será lançado um `HTTPError` com código de status 415. Também é fornecida
uma implementação para `list[pydantic.BaseModel]`.
