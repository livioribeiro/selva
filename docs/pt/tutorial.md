# Tutorial

Vamos nos aprofundar um pouco mais e a aprender os conceitos básicos.

Nós criaremos uma api de cumprimentos que salva logs das requisições.

## Instalando o Selva

Antes de seguir em frente, nós precisamos instalar o Selva e [Uvicorn](https://www.uvicorn.org/).

```shell
pip install selva uvicorn[standard]
```

## Estrutura da aplicação

Uma aplicação Selva pode ser estruturada das seguintes formas:

```
# mínimo
project/
├── application.py
├── configuration/
│   └── settings.yaml
└── resources/

# com módulos
project/
├── application/
│   ├── __init__.py
│   ├── handler.py
│   ├── repository.py
│   └── service.py
├── configuration/
│   └── settings.yaml
└── resources/
```

E é isso! Um módulo ou pacote chamado `application` será automaticamente importado
e escaneado para encontrar os tratadores e serviços.

Você ainda pode estruturar o `application` da forma que melhor te atender.

## Executando a aplicação

Nós usaremos o `uvicorn` para executar a aplicação e automaticamente reiniciar
quando fizermos mudanças no código:

```shell
$ uvicorn selva.run:app --reload
INFO:     Will watch for changes in these directories: ['/home/user/projects/selva-tutorial']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1001] using WatchFiles
INFO:     Started server process [1000]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Funções tratadoras

Funções tratadoras responderão a requisições HTTP ou WebSocket. Elas podem receber
serviços através do sistema de injeção de dependências.

=== "application/handler.py"

    ```python
    from typing import Annotated
    from asgikit.requests import Request
    from asgikit.responses import respond_json
    from selva.web import get, FromPath
    
    @get("hello/:name") # (1)
    async def hello(request: Request, name: Annotated[str, FromPath]):
        await respond_json(request.response, {"greeting": f"Hello, {name}!"})
    ```

    1.  `@get("hello/:name")` define a função como um tratador no caminho informado.
        Se um caminho não for fornecido, o caminho raiz ("/") será utilizado.

        `:name` define um parâmetro de caminho que será ligado ao parâmetro
        `name` no tratador, indicado por `Annotated[str, FromPath]`.

E agora nós testamos se nosso handler está funcionando:

```shell
$ curl localhost:8000/hello/World
{"greeting": "Hello, World!"}
```

Neste momento nosso handler apenas recebe um nome do caminho e responde com dados
JSON para o cliente.

## Criando o serviço Greeter

Nosso serviço terá um método que recebe um nome e retorna um cumprimento. Ele será
injetado no handler que nós criamos anteriormente.

=== "application/service.py"

    ```python
    from selva.di import service
    
    
    @service # (1)
    class Greeter:
        def greet(self, name: str) -> str:
            return f"Hello, {name}!"
    ```

    1.  `@service` registra a classe no sistema de injeção de dependências para
        que ele possa ser injetado em outras classes ou funções handler

=== "application/handler.py"

    ```python
    from typing import Annotated
    from asgikit.requests import Request
    from asgikit.responses import respond_json
    from selva.di import Inject
    from selva.web import get
    from .service import Greeter


    @get("/hello/:name")
    async def hello(
        request: Request,
        name: Annotated[str, FromPath],
        gretter: Annotated[Gretter, Inject], # (1)
    ):
        greeting = greeter.greet(name)
        await respond_json(request.response, {"greeting": greeting})
    ```

    1.  Injeta o serviço `Greeter`

## Adicionar um banco de dados

Nosso serviço de cumprimentos está funcionando bem, mas nós poderíamos querer registrar
as requisições de cumprimentos num banco de dados persistente, para realizar auditorias.

Para fazer isso nós precisamos criar um serviço de banco de dados e injetá-lo no
serviço `Greeter`. Para isso nós usaremos a biblioteca [Databases](https://www.encode.io/databases/)
com suporte a SQLite:

```shell
pip install databases[aiosqlite]
```

A biblioteca `databases` provê uma classe chamada `Database`. No entando, nós não
podemos decorá-la com `@service`, então precisaremos criar uma função factory:

=== "application/repository.py"

    ```python
    from datetime import datetime
    from typing import Annotated
    from databases import Database
    from selva.di import service, Inject
    
    @service # (1)
    async def database_factory() -> Database:
        database = Database("sqlite:///database.sqlite3")
        await database.connect()

        yield database

        await database.disconnect()


    @service
    class GreetingRepository:
        database: Annotated[Database, Inject] # (2)
    
        async def initialize(self): # (3)
            query = """
                create table if not exists greeting_log(
                    greeting text not null,
                    datetime text not null
                );
            """
            await database.execute(query)
    
        async def finalize(self): # (4)
            query = "drop table if exists greeting_log;"
            await database.execute(query)
    
        async def save_greeting(self, greeting: str, date: datetime):
            query = """
                insert into greeting_log (greeting, datetime)
                values (:greeting, datetime(:datetime))
            """
            params = {"greeting": greeting, "datetime": date}
            await self.database.execute(query, params)
    ```

    1.  A função decorada com `@service` é usada para criar o serviço quando você
        precisa prover tipos que você não detém o controle

    2.  Injetar o serviço `Database` no `GreetingRepository`

    3.  O método chamado `initialize` será chamado após o serviço ser construído
        para executar qualquer lógica de inicialização

    4.  O método chamado `finalize` será chamado antes que o serviço seja destruído
        para executar qualquer lógica de finalização.

=== "application/handler.py"

    ```python
    from typing import Annotated
    from datetime import datetime
    from asgikit.requests import Request
    from asgikit.responses import respond_json
    from selva.di import Inject
    from selva.web import get, FromPath
    from .repository import GreetingRepository
    from .service import Greeter


    @get("hello/:name")
    async def hello_name(
        request: Request,
        name: Annotated[str, FromPath],
        greeter: Annotated[Greeter, Inject],
        repository: Annotated[GreetingRepository, Inject],
    ):
        greeting = greeter.greet(name)
        await repository.save_greeting(greeting, datetime.now())
        await respond_json(request.response, {"greeting": greeting})
    ```

## Executar ações após o envio da resposta

Os cumprimentos estão sendo salvos no banco de dados, mas agora nós temos um problema:
O usuário precisa esperar até que o cumprimento seja salvo antes de recebê-lo.

Para resolver esse problema e melhorar a experiência do usuário, nós podemos salvar
o cumprimento após a requisição ser concluída:

=== "application/handler.py"

    ```python
    from datetime import datetime
    from typing import Annotated
    from asgikit.requests import Request
    from asgikit.responses improt respond_json
    from selva.di import Inject
    from selva.web import get, FromPath
    from .repository import GreetingRepository
    from .service import Greeter


    @get("hello/:name")
    async def hello_name(
        request: Request,
        name: Annotated[str, FromPath],
        greeter: Annotated[Greeter, Inject],
        repository: Annotated[GreetingRepository, Inject],
    ):
        greeting = greeter.greet(name)
        await respond_json(request.response, {"greeting": greeting})  # (1)

        await repository.save_greeting(greeting, datetime.now())  # (2)
    ```

    1.  A chamada a `respond_json` conclui a resposta

    2.  O cumprimento é salvo após a resposta ser enviada

## Recuperando os logs de cumprimentos

Para ver os cumprimentos salvos no banco de dados, nós precisamos apenas adicionar
um handler para recuperar os logs e retorná-los:

=== "application/repository.py"

    ```python
    @service
    class GreetingRepository:
        # ...
        async def get_greetings(self) -> list[tuple[str, str]]:
            query = """
                select l.greeting, datetime(l.datetime) from greeting_log l
                order by rowid desc
            """
            result = await self.database.fetch_all(query)
            return [{"greeting": r.greeting, "datetime": r.datetime} for r in result]
    ```

=== "application/handler.py"

    ```python
    # ...
    @get("/logs")
    async def greeting_logs(
        request: Request,
        repository: Annotated[GreetingRepository, Inject],
    ):
        greetings = await repository.get_greetings()
        await respond_json(request.response, greetings)
    ```

Agora nós podemos tentar requisitar alguns cumprimentos e recuperar os logs:

```shell
$ curl localhost:8000/hello/Python
{"greeting": "Hello, Python!"}

$ curl localhost:8000/hello/World
{"greeting": "Hello, World!"}

$ curl -s localhost:8000/logs | python -m json.tool
[
    {
        "greeting": "Hello, World!",
        "datetime": "2025-01-01 12:00:10"
    },
    {
        "greeting": "Hello, Python!",
        "datetime": "2025-01-01 12:00:20"
    },
]
```

## Recebendo dados de post

Nós também podemos enviar o nome no corpo da requisição, ao invés da url, e usar
o Pydantic para tratar o corpo da requisição:

=== "application/models.py"

    ```python
    from pydantic import BaseModel
    
    
    class GreetingRequest(BaseModel):
        name: str
    ```

=== "application/handler.py"

    ```python
    # ...
    from selva.web import FromBody
    from .model import GreetingRequest

    # ...

    @post("hello")
    async def hello_post(
        request: Request,
        greeting_request: Annotated[GreetingRequest, FromBody],
        greeter: Annotated[Greeter, Inject],
        repository: Annotated[GreetingRepository, Inject],
    ):
        name = greeting_request.name
        greeting = greeter.greet(name)
        await respond_json(request.response, {"greeting": greeting})
        await repository.save_greeting(greeting, datetime.now())
    ```

E para testar:

```shell
$ curl -H 'Content-Type: application/json' -d '{"name": "World"}' localhost:8000/hello
{"greeting": "Hello, World!"}
```