# Tutorial

Let's dig a little deeper and learn the basic concepts of Selva.

We will create a greeting api that logs the greet requests.

## Installing Selva

Before going any further, we need to install Selva and [Uvicorn](https://www.uvicorn.org/).

```shell
pip install selva uvicorn[standard]
```

## Structure of the application

A selva application can be structured like the following:

```
# mininal
project/
├── application.py
├── configuration/
│   └── settings.yaml
└── resources/

# with modules
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

And... that's it! A module or package named `application` will automatically
be imported and scanned for handlers and services.

You can structure the `application` package however suits you.

## Running the application

We will use `uvicorn` to run the application and automatically reload when we
make changes to the code:

```shell
$ uvicorn selva.run:app --reload
INFO:     Will watch for changes in these directories: ['/home/user/projects/selva-tutorial']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1001] using WatchFiles
INFO:     Started server process [1000]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Handler functions

Handler functions will respond to HTTP or WebSocket requests. They can receive services
through dependency injection.

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
    
    1.  `@get("hello/:name")` defines the function as a handler on the given path.
        If no path is given, the root path ("/") will be used.
    
        `:name` defines a path parameter that will be bound to the `name`
        parameter on the handler, indicated by `Annotated[str, FromPath]`

And now we test if our handler is working:

```shell
$ curl localhost:8000/hello/World
{"greeting": "Hello, World!"}
```

Right now our handler just get a name from the path and respond with JSON data to
the client.

## Creating the Greeter service

Our service will have a method that receives a name and returns a greeting. It
will be injected into the handler we created previously.

=== "application/service.py"

    ```python
    from selva.di import service
    
    
    @service # (1)
    class Greeter:
        def greet(self, name: str) -> str:
            return f"Hello, {name}!"
    ```

    1.  `@service` registers the class in the dependency injection system so it
        can be injected in other classes or handler functions

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

    1.  Inject the `Greeter` service

## Adding a database

Our greeting application is working fine, but we might want to register
the greeting requests in a persistent database, for auditing purposes.

To do this we need to create the database service and inject it into the
`Greeter` service. For this we can use the [Databases](https://www.encode.io/databases/)
library with SQLite support:

```shell
pip install databases[aiosqlite]
```

`Databases` provides a class called `Database`. However, we can not decorate it
with `@service`, so in this case we need to create a factory function for it:

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

    1.  A function decorated with `@service` is used to create a service when
        you need to provide types you do not own

    2.  Inject the `Database` service in the `GreetingRepository`

    3.  A method called `initialize` will be called after the service is
        constructed in order to run any initialization logic

    4.  A method called `finalize` will be called before the service is
        destroyed in order to run any cleanup logic

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

## Execute actions after response

The greetings are being saved to the database, but now we have a problem: the
user has to wait until the greeting is saved before receiving it.

To solve this problem and improve the user experience, we can save the greeting
after the request is completed:

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
    
    1.  The call to `respond_json` completes the response
    
    2.  The greeting is saved after the response is completed

## Retrieving the greeting logs

To see the greetings saved to the database, we just need to add a handler to get
the logs and return them:

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

Now let us try requesting some greetings and retrieving the logs:

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

## Receiving post data

We can also send the name in the body of the request, instead of the url, and
use Pydantic to parse the request body:

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

And to test it:

```shell
$ curl -H 'Content-Type: application/json' -d '{"name": "World"}' localhost:8000/hello
{"greeting": "Hello, World!"}
```