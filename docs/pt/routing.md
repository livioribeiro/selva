# Roteamento

Roteamento é definido pelos decoradores nos handlers.

## Parâmetros de caminho

Parâmetros podem ser definidos no caminho dos handlers utilizando a sintaxe `:parameter_name`,
onde `parameter_name` deve ser o nome do argumento na assinatura do handler.

```python
from typing import Annotated
from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import get, FromPath


@get("hello/:name")
async def handler(request: Request, name: Annotated[str, FromPath]):
    await respond_text(request.response, f"Hello, {name}!")
```

Aqui foi usado `Annotated` e `FromPath` para indicar que o argumento do handler
deve ser vinculado ao parâmetro do caminho da requisição. Mais sobre isso será explicado
nas seções seguintes.

## Correspondência de caminho

O comportamento padrão é o parâmetro de caminho corresponder a apenas um único seguimento.
Se você quiser corresponder ao caminho completo, ou a um subcaminho do caminho da
requisição, utilize a sintaxe `*parameter_name`.

```python
from typing import Annotated
from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import get, FromPath


@get("hello/*path")
async def handler(request: Request, path: Annotated[str, FromPath]):
    name = " ".join(path.split("/"))
    await respond_text(request.response, f"Hello, {name}!")
```

Para uma requisição como `GET hello/Python/World`, o handler retornará
`Hello, Python World!`.

Você pode combinar ambos os tipos de parâmetros sem problemas:

- `*path`
- `*path/literal_segment`
- `:normal_param/*path`
- `:normal_param/*path/:other_path`

## Conversão de parâmetros

A conversão de parâmetros é realizada através de anotações de tipo nos parâmetros.
O framework tentará encontrar um conversor adequado ao tipo do parâmetro e então
converter o valor antes de chamar o handler.

```python
from typing import Annotated
from asgikit.requests import Request
from asgikit.responses import respond_json
from selva.web import get, FromPath


@get("repeat/:amount")
async def handler(request: Request, amount: Annotated[int, FromPath]):
    await respond_json(request.response, {f"repeat {i}": i for i in range(amount)})
```

O framework procurará por um serviço que implementa `selva.web.converter.from_request.FromRequest[FromPath]`
para recuperar os dados da requisição, então esse serviço procurará por um conversor,
um serviço que implementa `selva.web.converter.Converter[str, int]` para converter
os dados para o tipo requisitado.

Selva provê conversores para os tipos `str`, `int`, `float`, `bool` e `pathlib.PurePath`.

## Coversão de parâmetros customizada

A conversão pode ser customizada ao prover uma implementação de `selva.web.converter.Converter`.
Você normalmente utilizará como atalho o decorador `selva.web.converter.decorator.register_converter.`

```python
from dataclasses import dataclass
from typing import Annotated

from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import get, FromPath
from selva.web.converter.decorator import register_converter


@dataclass
class MyModel:
    name: str


@register_converter(str, MyModel)
class MyModelParamConverter:
    def convert(self, value: str) -> MyModel:
        return MyModel(value)


@get("/:model")
async def handler(request: Request, model: Annotated[MyModel, FromPath]):
    await respond_text(request.response, str(model))
```

Se a implementação de `Converter` lançar um erro, o handler não será chamado.
E se o erro for uma subclasse de `selva.web.error.HTTPError`, por exemplo,
`HTTPUnauthorizedException`, uma resposta será produzida de acordo com o erro.
