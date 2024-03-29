# SQLAlchemy

The SQLAlchemy extension makes it easy to set up database connections, providing
the classes `AsyncEngine` and `async_sessionmaker` as services in the dependency
injection context.

## Usage

Install SQLAlchemy extra and a database driver that supports async:

```shell
pip install selva[sqlalchemy] aiosqlite asyncpg aiomysql oracledb
```

Define the configuration properties:

```yaml
extensions:
  - selva.ext.data.sqlalchemy # (1)

data:
  sqlalchemy:
    default: # (2)
      url: "sqlite+aiosqlite:///var/db.sqlite3"

    postgres: # (3)
      url: "postgresql+asyncpg://user:pass@localhost/dbname"

    mysql: # (4)
      url: "mysql+aiomysql://user:pass@localhost/dbname"

    oracle: # (5)
      url: "oracle+oracledb_async://user:pass@localhost/DBNAME"
      # or "oracle+oracledb_async://user:pass@localhost/?service_name=DBNAME"
```

1.  Activate the sqlalchemy extension
2.  "default" connection will be registered without a name
3.  Connection registered with name "postgres"
4.  Connection registered with name "mysql"
5.  Connection registered with name "oracle"

And inject the `async_sessionmaker` services:

```python
from typing import Annotated
from sqlalchemy.ext.asyncio import async_sessionmaker
from selva.di import service, Inject


@service
class MyService:
    # default service
    sessionmaker: Annotated[async_sessionmaker, Inject]

    # named services
    sessionmaker_postgres: Annotated[async_sessionmaker, Inject(name="postgres")]
    sessionmaker_mysql: Annotated[async_sessionmaker, Inject(name="mysql")]
    sessionmaker_oracle: Annotated[async_sessionmaker, Inject(name="oracle")]
```

Database connections can also be defined with username and password separated from
the url, or even with individual components:

```yaml
data:
  sqlalchemy:
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

1.  Username and password separated from the database url
2.  Each component defined individually
3.  Query parameters can be define in a map
4.  "service_name" query parameter can be used instead of "database"
    ```yaml
    query:
      service_name: DBNAME
    ```

## Using environment variables

=== "configuration/settings.yaml"
    ```yaml
    data:
      sqlalchemy:
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
    
    1.  Can be define with just the environment variable `SELVA__DATA__SQLALCHEMY__DEFAULT__URL`
    2.  Can be defined with just the environment variables:
        - `SELVA__DATA__SQLALCHEMY__OTHER__URL`
        - `SELVA__DATA__SQLALCHEMY__OTHER__USERNAME`
        - `SELVA__DATA__SQLALCHEMY__OTHER__PASSWORD`
    3.  Can be defined with just the environment variables:
        - `SELVA__DATA__SQLALCHEMY__ANOTHER__DRIVERNAME`
        - `SELVA__DATA__SQLALCHEMY__ANOTHER__HOST`
        - `SELVA__DATA__SQLALCHEMY__ANOTHER__PORT`
        - `SELVA__DATA__SQLALCHEMY__ANOTHER__DATABASE`
        - `SELVA__DATA__SQLALCHEMY__ANOTHER__USERNAME`
        - `SELVA__DATA__SQLALCHEMY__ANOTHER__PASSWORD`

## Example

=== "application/controller.py"

    ```python
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine

    from asgikit.responses import respond_json

    from selva.di import Inject
    from selva.web import controller, get

    from .model import Base, MyModel


    @controller
    class Controller:
        engine: Annotated[AsyncEngine, Inject]
        sessionmaker: Annotated[async_sessionmaker, Inject]

        async def initialize():
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            async with self.sessionmaker() as session:
                my_model = MyModel(name="MyModel")
                session.add(my_model)
                await session.commit()
    
        @get
        async def index(request):
            async with self.sessionmaker() as session:
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

## Configuration options

Selva offers several options to configure SQLAlchemy. If you need more control over
the SQLAlchemy services, you can create your own `engine` and `sessionmaker` outside
of the DI context.

The available options are shown below:

```yaml
data:
  sqlalchemy:
    default:
      url: ""
      options: # (1)
        connect_args: # (2)
          arg: value
        echo: false
        echo_pool: false
        enable_from_linting: false
        hide_parameters: false
        insertmanyvalues_page_size: 1
        isolation_level: ""
        json_deserializer: "json.loads" # dotted path to the json deserialization function
        json_serializer: "json.dumps" # dotted path to the json serialization function
        label_length: 1
        logging_name: ""
        max_identifier_length: 1
        max_overflow: 1
        module: ""
        paramstyle: "qmark" # or "numeric", "named", "format", "pyformat"
        poolclass: "sqlalchemy.pool.Pool" # dotted path to the pool class
        pool_logging_name: ""
        pool_pre_ping: false
        pool_size: 1
        pool_recycle: 3600
        pool_reset_on_return: "rollback" # or "commit"
        pool_timeout: 1
        pool_use_lifo: false
        plugins:
          - "plugin1"
          - "plugin2"
        query_cache_size: 1
        use_insertmanyvalues: false
        execution_options: # (3)
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

1.  `options` values are described in [`sqlalchemy.create_engine`](https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine)
2.  `connect_args` is a map of args to pass to the `connect` function of the underlying driver
3.  `execution_options` values are describe in [`Sqlalchemy.engine.Connection.execution_options`](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection.execution_options)
