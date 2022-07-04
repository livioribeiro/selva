# Tutorial

Let's dig a little deeper and learn the basic concepts of Selva.

We will create a greeting api that logs the greet requests.

## Installing Selva

Before going any further, we need to install Selva and Uvicorn

```shell
pip install selva uvicorn
```

## Structure of the application

A selva application is structured like the following:

```
project/
├── application/
│   ├── __init__.py
│   ├── controllers.py
│   └── services.py
├── configuration/
│   └── application.toml
├── resources/
└── main.py
```

The `main.py` is just the entrypoint of the application.

```python
from selva.web import Application
app = Application()
```

And... that's it! Any module or package named `application` will automatically
be imported and scanned for controllers and services.

## Creating the GreetingController

Controller classes hold handler methods that will respond to HTTP or WebSocket
requests. They can receive services through dependency injection.

```python
### application/controllers.py

from selva.web import RequestContext, controller, get


@controller
class GreetingController:
    @get
    def hello(self, context: RequestContext):
        name = context.query.get("name", "World")
        return {"greeting": f"Hello, {name}!"}
```

Right now our controller just get a name from the query string and return a
`dict`. When a handler returns a `dict` or a `list` it will be automatically converted to JSON.

Let's move the greeting logic to a service.

## Creating the Greeter service

Our service will have a method that receives a name or `None` and returns a
greeting. It will be injected into the controller we created previously.

```python
### application/services.py
from selva.di import service

DEFAULT_NAME = "World"


@service
class Greeter:
    def greet(self, name: str | None) -> str:
        return f"Hello, {name or DEFAULT_NAME}!"
```

And now we change our controller to use the `GreeterService`:

```python
### application/controllers.py
from selva.web import RequestContext, controller, get

from .services import Greeter


@controller
class GreetingController:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get
    def hello(self, context: RequestContext):
        name = context.query.get("name", None)
        greeting = self.greeter.greet(name)
        return {"greeting": greeting}
```

## Add a database

Our greeting application is workign fine, but we might want to add register
the greeting requests in a persistent database, for auditing purposes.

To do this we need to create the database service and inject it into the
Greeter service. For this we can use the [Databases](https://www.encode.io/databases/)
library with SQLite support:

```shell
pip install databases[aiosqlite]
```

`Databases` provides a class called `Database`. However, we can not decorate it
with `@service`, so in this case we need to create a factory function for it:

```python
### application/services.py
from selva.di import service, initializer, finalizer
from databases import Database

DEFAULT_NAME = "World"


@service
def database_factory() -> Database:
    database = Database("sqlite:///database.sqlite3")
    database.execute("""
        create table if not exists greeting_log(
            id integer auto increment primary key,
            name text not null,
            date text not null default datetime(),
        );
    """)
    return database


@service
class Greeter:
    def __init__(self, database: Database):
        self.database = database

    @initializer
    async def initialize(self):
        await self.database.connect()

    @finalizer
    async def finalize(self):
        await self.database.disconnect()

    async def save_log(self, name: str):
        await self.database.execute(
            "insert into greeting_log (name) values (:name)",
            {"name": name},
        )

    async def greet(self, name: str | None) -> str:
        greeted_name = name or DEFAULT_NAME
        await self.save_log(greeted_name)
        return f"Hello, {greeted_name}!"
```
