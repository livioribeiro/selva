# SQLAlchemy

A estensão do SQLAlchemy facilita a configuração de conexões com bancos de dados,
provendo os `AsyncEngine` e `async_sessionmaker` como serviços no context de injeção
de dependências.

## Utilização

Instale o extra `sqlalchemy` e um driver de banco de dados que suporta _async_:

```shell
pip install selva[sqlalchemy] aiosqlite asyncpg aiomysql oracledb
```

Com os drivers instalados, nós podemos definir as conexões no arquivo de configuração:

```yaml
extensions:
  - selva.ext.data.sqlalchemy # (1)

middleware:
  - selva.ext.data.sqlalchemy.middleware.scoped_session # (2)

data:
  sqlalchemy:
    connections:
      default: # (3)
        url: "sqlite+aiosqlite:///var/db.sqlite3"

      postgres: # (4)
        url: "postgresql+asyncpg://user:pass@localhost/dbname"

      mysql: # (5)
        url: "mysql+aiomysql://user:pass@localhost/dbname"

      oracle: # (6)
        url: "oracle+oracledb_async://user:pass@localhost/DBNAME"
        # ou "oracle+oracledb_async://user:pass@localhost/?service_name=DBNAME"
```

1.  Ativar a extensão sqlalchemy
2.  Ativar o middleware de scoped session
3.  A conexão "default" será registrada sem um nome
4.  Conexão registrada com nome "postgres"
5.  Conexão registrada com nome "mysql"
6.  Conexão registrada com nome "oracle"

Uma vez definidas as conexões, nós podemos injetar `AsyncEngine` nos nossos serviços.
Para cada conexão, uma instância de `AsyncEngine` será registrada, a conexão `default`
será registrada sem um nome, e as outras conexões serão registradas com seus respectivos
nomes.

```python
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncEngine
from selva.di import service, Inject


@service
class MyService:
    # default service
    engine: Annotated[AsyncEngine, Inject]

    # named services
    engine_postgres: Annotated[AsyncEngine, Inject("postgres")]
    engine_mysql: Annotated[AsyncEngine, Inject("mysql")]
    engine_oracle: Annotated[AsyncEngine, Inject("oracle")]
```

## Scoped Session

Se o middleware `selva.ext.data.sqlalchemy.middleware.scoped_session` for ativado,
o serviço `selva.ext.data.sqlalchemy.ScopedSession` será registrado. Ele provê acesso
a uma instância de `AsyncSession` que fica disponível pela duração da requisição.

```python
from typing import Annotated
from sqlalchemy import text
from selva.di import service, Inject
from selva.ext.data.sqlalchemy import ScopedSession


@service
class MyService:
    session: Annotated[ScopedSession, Inject]

    async def method(self) -> int:
        return await self.session.scalar(text("select 1"))
```

O serviço `ScopedSession` é um proxy para a instância de `AsyncSession` que é criado
pelo middeware `selva.ext.data.sqlalchemy.middleware.scoped_session`.

## Configuração

Conexões de bancos de dados podem ser definidas com usuário e senha separados da
url, ou até com componentes individuais:

```yaml
data:
  sqlalchemy:
    connections:
      default:
        drivername: sqlite+aiosqlite
        database: "/var/db.sqlite3"

      postgres: # (1)
        url: "postgresql+asyncpg://localhost/dbname"
        username: user
        password: pass

      mysql: # (2)
        drivername: mysql+aiomysql
        host: localhost
        port: 3306
        database: dbname
        username: user
        password: pass

      oracle: # (3)
        drivername: oracle+oracledb_async
        host: localhost
        port: 1521
        database: DBNAME # (4)
        username: user
        password: pass
```

1.  Usuário e senha separados da url
2.  Cada componente definido individualmente
3.  Parâmetros de query podem ser definidos em um mapa
4.  Parâmetro de query "service_name" pode ser usado ao invés de "database"
    ```yaml
    query:
      service_name: DBNAME
    ```

## Utilizando variáveis de ambiente

É uma boa prátia externalizar configurações através de variáveis de ambiente. Nós
podemos referencias variáveis na configuração ou utilizar variáveis com prefixo
`SELVA__`, por exemplo, `SELVA__DATA__SQLALCHEMY__CONNECTIONS__DEFAULT__URL`.

=== "configuration/settings.yaml"
    ```yaml
    data:
      sqlalchemy:
        connections:
          default:
            url: "${DATABASE_URL}" # (1)

          other: # (2)
            url: "${DATABASE_URL}"
            username: "${DATABASE_USERNAME}"
            password: "${DATABASE_PASSWORD}"
    
          another: # (3)
            drivername: "${DATABASE_DRIVERNAME}"
            host: "${DATABASE_HOST}"
            port: ${DATABASE_PORT}
            database: "${DATABASE_NAME}"
            username: "${DATABASE_USERNAME}"
            password: "${DATABASE_PASSWORD}"
    ```
    
    1.  Pode ser definido com a variável de ambiente `SELVA__DATA__SQLALCHEMY__DEFAULT__URL`
    2.  Pode ser definido com as variáveis de ambiente:
        - `SELVA__DATA__SQLALCHEMY__CONNECTIONS__OTHER__URL`
        - `SELVA__DATA__SQLALCHEMY__CONNECTIONS__OTHER__USERNAME`
        - `SELVA__DATA__SQLALCHEMY__CONNECTIONS__OTHER__PASSWORD`
    3.  Pode ser definido com as variáveis de ambiente:
        - `SELVA__DATA__SQLALCHEMY__CONNECTIONS__ANOTHER__DRIVERNAME`
        - `SELVA__DATA__SQLALCHEMY__CONNECTIONS__ANOTHER__HOST`
        - `SELVA__DATA__SQLALCHEMY__CONNECTIONS__ANOTHER__PORT`
        - `SELVA__DATA__SQLALCHEMY__CONNECTIONS__ANOTHER__DATABASE`
        - `SELVA__DATA__SQLALCHEMY__CONNECTIONS__ANOTHER__USERNAME`
        - `SELVA__DATA__SQLALCHEMY__CONNECTIONS__ANOTHER__PASSWORD`

## Trabalhando com async_sessionmaker

Diferente do `AsyngEngine`, Selva cria apenas um único `async_sessionmaker`. Nós
podemos associar subclases específicas de `DeclarativeBase` através da configuração
`data.sqlalchemy.session.binds`, caso contrário será associado à conexão `default`.

=== "application/model.py"

    ```python
    from sqlalchemy.orm import DeclarativeBase
    
    
    class Base(DeclarativeBase):
        pass
    
    
    class OtherBase(DeclarativeBase):
        pass
    ```

=== "configuration/settings.yaml"

    ```yaml
    data:
      sqlalchemy:
        connections:
          default:
            url: "sqlite+aiosqlite://db1.sqlite3"
          other:
            url: "sqlite+aiosqlite://db2.sqlite3"
        session:
          binds:
            application.model.Base: default
            application.model.OtherBase: other
    ```

## Examplo

=== "application/handler.py"

    ```python
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

    from asgikit.responses import respond_json

    from selva.di import Inject
    from selva.web import get

    from .model import Base, MyModel
    
    
    @get
    async def index(
        request,
        engine: Annotated[AsyncEngine, Inject],
        sessionmaker: Annotated[async_sessionmaker, Inject],
    ):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with sessionmaker() as session:
            my_model = MyModel(name="MyModel")
            session.add(my_model)
            await session.commit()

        async with sessionmaker() as session:
            my_model = await session.scalar(select(MyModel).limit(1))
            await respond_json(request.response, {
                "id": my_model.id,
                "name": my_model.name,
            })
    ```

=== "application/model.py"

    ```python
    from sqlalchemy import Column, Integer, String
    from sqlalchemy.orm import DeclarativeBase
    
    
    class Base(DeclarativeBase):
        pass
    
    
    class MyModel(Base):
        __tablename__ = 'my_model'
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(length=100))
    
        def __repr__(self):
            return f"<MyModel(id={self.id}, name={self.name})>"
    ```

=== "configuration/settings.yaml"

    ```yaml
    data:
      sqlalchemy:
        default:
          url: "sqlite+aiosqlite://:memory:"
    ```

## Opções de configuração

Selva oferece várias opções para configurar o SQLAlchemy. Se você precisar de mais
controle sobre os serviços do SQLAlchemy, você pode criar os seus próprios serviços
`AsyncEngine` e `async_sessionmaker`.

As opções disponíveis são mostradas abaixo:

```yaml
data:
  sqlalchemy:
    session:
      options: # (1)
        class: sqlalchemy.ext.asyncio.AsyncSession
        autoflush: true
        expire_on_commit: true
        autobegin: true
        twophase: false
        enable_baked_queries: true
        info: # (2)
          field: "value"
        # info: "package.module.variable"
        query_cls: "sqlalchemy.orm.query.Query"
        join_transaction_mode: "conditional_savepoint" # ou "rollback_only", "control_fully", "create_savepoint"
        close_resets_only: null
      binds: # (3)
        application.model.Base: default
        application.model.OtherBase: other
    connections:
      default:
        url: ""
        options: # (4)
          connect_args: "package.module.variable" # (5)
          echo: false
          echo_pool: false
          enable_from_linting: false
          hide_parameters: false
          insertmanyvalues_page_size: 1
          isolation_level: ""
          # caminho para a função de desserialização json
          json_deserializer: "json.loads"
          # caminho para a função de serialização json
          json_serializer: "json.dumps"
          label_length: 1
          logging_name: ""
          max_identifier_length: 1
          max_overflow: 1
          module: ""
          paramstyle: "qmark" # ou "numeric", "named", "format", "pyformat"
          # caminho para classe python
          poolclass: "sqlalchemy.pool.Pool"
          pool_logging_name: ""
          pool_pre_ping: false
          pool_size: 1
          pool_recycle: 3600
          pool_reset_on_return: "rollback" # ou "commit"
          pool_timeout: 1
          pool_use_lifo: false
          plugins:
            - "plugin1"
            - "plugin2"
          query_cache_size: 1
          use_insertmanyvalues: false
          execution_options: # (5)
            logging_token: ""
            isolation_level: ""
            no_parameters: false
            stream_results: false
            max_row_buffer: 1
            yield_per: 1
            insertmanyvalues_page_size: 1
            schema_translate_map:
              null: "my_schema"
              some_schema: "other_schema"
```

1.  Valores são descritos em [`sqlalchemy.orm.Session`](https://docs.sqlalchemy.org/orm/session_api.html#sqlalchemy.orm.Session)
2.  Pode ser um mapa ou um caminho para uma variável python contendo um `dict`
3.  Associa subclasses de `sqlalchemy.orm.DeclarativeBase` a nomes de conexões definidas
    em `connections`
4.  Valores são descritos em [`sqlalchemy.create_engine`](https://docs.sqlalchemy.org/core/engines.html#sqlalchemy.create_engine)
5.  `connect_args` é um caminho para um `dict[str, Any]` que será provido como argumentos
    para a função `connect` do driver do banco de dados
6.  Valores de `execution_options` são descritos em [`Sqlalchemy.engine.Connection.execution_options`](https://docs.sqlalchemy.org/core/connections.html#sqlalchemy.engine.Connection.execution_options)
