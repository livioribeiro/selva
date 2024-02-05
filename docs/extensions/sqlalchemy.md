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
