# SQLAlchemy

The SQLAlchemy extension makes it easy to set up database connections, providing
the classes `AsyncEngine` and `async_sessionmaker` as services in the dependency
injection context.


## Usage

Install SQLAlchemy python package and the database driver:

```shell
pip install sqlalchemy aiosqlite aiomysql psycopg oracledb
```

Define the configuration properties for the database:

=== "configuration/settings.yaml"
    ```yaml
    data:
      sqlalchemy:
        default: # (1)
          url: "sqlite+aiosqlite:///opt/db.sqlite3"
    
        postgres: # (2)
          url: "postgresql+psycopg://user:pass@localhost/dbname"
    
        mysql:
          url: "mysql+aiomysql://user:pass@localhost/dbname"
    
        oracle:
          url: "oracle+oracledb_async://user:pass@localhost/?service_name=XEPDB1"
    ```
    
    1.  "default" connection will be registered without name
    2.  Will be registered as "postgres"

=== "application/service.py"
    ```python
    from typing import Annotated
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from selva.di import service, Inject
    
    
    @service
    class MyService:
        sessionmaker: Annotated[async_sessionmaker, Inject]
        sessionmaker_postgres: Annotated[async_sessionmaker, Inject(name="postgres")]
        sessionmaker_mysql: Annotated[async_sessionmaker, Inject(name="mysql")]
        sessionmaker_oracle: Annotated[async_sessionmaker, Inject(name="oracle")]
    ```

Database connection can also be defined with username and password separated from
the url, or even with individual components:

=== "configuration/settings.yaml"
    ```yaml
    data:
      sqlalchemy:
        url_username_password: # (1)
          url: "postgresql+psycopg://localhost/dbname"
          username: user
          password: pass
    
        url_components: # (2)
          drivername: postgresql+psycopg
          host: localhost
          port: 5432
          database: dbname
          username: user
          password: pass
    ```

    1.  Username and password separated from the database url
    2.  Each component defined individually

Using environment variables to configure the connections:

=== "configuration/settings.yaml"
    ```yaml
    data:
      sqlalchemy:
        default:
          url: "${DATABASE_URL}"

        url_username_password:
          url: "${DATABASE_URL}"
          username: "${DATABASE_USERNAME}"
          password: "${DATABASE_PASSWORD}"
    
        url_components:
          drivername: postgresql+psycopg
          host: "${DATABASE_HOST}"
          port: ${DATABASE_PORT}
          database: "${DATABASE_NAME}"
          username: "${DATABASE_USERNAME}"
          password: "${DATABASE_PASSWORD}"
    ```

## Connection Options

It is possible to pass options to the SQLAlchemy connection. One notable option
is connection pool settings. The available options managed by Selva are:

```yaml
data:
  sqlalchemy:
    default:
      url: ""
      options: # (1)
        creator: ""
        echo: false
        echo_pool: false
        enable_from_linting: false
        hide_parameters: false
        insertmanyvalues_page_size: 1
        isolation_level: ""
        json_deserializer: "json.loads"
        json_serializer: "json.dumps"
        label_length: 1
        logging_name: ""
        max_identifier_length: 1
        max_overflow: 1
        module: "psycopg"
        paramstyle: "qmark" # or "numeric", "named", "format", "pyformat"
        poolclass: "sqlalchemy.pool.Pool"
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
        execution_options: # (2)
          logging_token: ""
          isolation_level: ""
          no_parameters: false
          stream_results: false
          max_row_buffer: 1
          yield_per: 1
          insertmanyvalues_page_size: 1
          schema_translate_map:
            key: "value"
            other_key: "other value"
```

1.  `options` values are described in [`sqlalchemy.create_engine`](https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine)
2.  `execution_options` values are describe in [`qlalchemy.engine.Connection.execution_options`](https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Connection.execution_options)