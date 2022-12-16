# Tutorial

Let's dig a little deeper and learn the basic concepts of Selva.

We will create a greeting api that logs the greet requests.

## Installing Selva

Before going any further, we need to install Selva and [Uvicorn](https://www.uvicorn.org/).

```shell
pip install selva uvicorn
```

## Structure of the application

A selva application is structured like the following:

```
project/
├── application/
│   ├── __init__.py
│   ├── controller.py
│   ├── repository.py
│   └── service.py
├── configuration/
│   └── application.toml
├── resources/
```

And... that's it! A module or package named `application` will automatically
be imported and scanned for controllers and services.

## Running the application

We will use `uvicorn` to run the application and automatically reload when we
make changes to the code:

```shell
$ uvicorn selva.run:app --reload
INFO:     Will watch for changes in these directories: ['/home/user/projects/selva-tutorial']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [23568] using WatchFiles
INFO:     Started server process [19472]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Creating the GreetingController

Controller classes hold handler methods that will respond to HTTP or WebSocket
requests. They can receive services through dependency injection.

=== "application/controller.py"

    ```python
    from selva.web import controller, get
    
    
    @controller # (1)
    class GreetingController:
        @get("hello/:name") # (2)
        def hello(self, name: str) -> dict:
            return {"greeting": f"Hello, {name}!"}
    ```

    1.  `@controller` marks a class as a controller. It can optionally receive
        a path (e.g. `@controller("path")`) that will be prepended to the handlers' path.

    2.  `@get("hello/:name")` defines the method as a handler on the given path.
        If no path is given, the path from the controller will be used.

        `:name` defines a path parameter that will be bound to the `name`
        parameter on the handler

And now we test if our controller is working:

```shell
$ curl localhost:8000/hello/World
{"greeting": "Hello, World!"}
```

Right now our controller just get a name from the query string and return a
`dict`. When a handler returns a `dict` or a `list` it will be automatically
converted to JSON.

## Creating the Greeter service

Our service will have a method that receives a name and returns a greeting. It
will be injected into the controller we created previously.

=== "/application/service.py"

    ```python
    from selva.di import service
    
    
    @service # (1)
    class Greeter:
        def greet(self, name: str) -> str:
            return f"Hello, {name}!"
    ```

    1.  `@service` registers the class in the dependency injection system so it
        can be injected in other classes

=== "application/controller.py"

    ```python
    from selva.di import Inject
    from selva.web import controller, get
    from .service import Greeter
    
    
    @controller
    class GreetingController:
        gretter: Gretter = Inject() # (1)
    
        @get("/hello/:name")
        def hello_name(self, name: str) -> dict:
            greeting = self.greeter.greet(name)
            return {"greeting": greeting}
    ```
    
    1.  Inject the `Greeter` service in the constructor

## Adding a database

Our greeting application is working fine, but we might want to add register
the greeting requests in a persistent database, for auditing purposes.

To do this we need to create the database service and inject it into the
Greeter service. For this we can use the [Databases](https://www.encode.io/databases/)
library with SQLite support:

```shell
pip install databases[aiosqlite]
```

`Databases` provides a class called `Database`. However, we can not decorate it
with `@service`, so in this case we need to create a factory function for it:

=== "application/repository.py"

    ```python
    from datetime import datetime
    from databases import Database
    from selva.di import service, Inject
    
    @service # (1)
    async def database_factory() -> Database:
        database = Database("sqlite:///database.sqlite3")
        query = """
            create table if not exists greeting_log(
                greeting text not null,
                datetime text not null
            );
        """
        await database.execute(query)
        return database
    
    
    @service
    class GreetingRepository:
        database: Database = Inject() # (2)
    
        async def initialize(self): # (3)
            await self.database.connect()
    
        async def finalize(self): # (4)
            await self.database.disconnect()
    
        async def save_greeting(self, greeting: str, date: datetime):
            query = """
                insert into greeting_log (greeting, datetime)
                values (:greeting, datetime(:datetime))
            """
            params = {"greeting": greeting, "datetime": date}
            await self.database.execute(query, params)
    ```

    1.  A function decorated with `@service` can used to create a service when
        you need to provide types you do not own

    2.  Inject the `Database` service in the `GreetingRepository`

    3.  A method called `initialize` will be invoked after the service is
        constructed in order to run any initialization logic

    4.  A method called `finalize` will be invoked before the service is
        destroyed in order to run any cleanup logic

=== "application/controller.py"

    ```python
    from datetime import datetime
    from selva.di import Inject
    from selva.web import controller, get
    from .repository import GreetingRepository
    from .service import Greeter
    
    
    @controller
    class GreetingController:
        greeter: Greeter = Inject()
        repository: GreetingRepository = Inject()
    
        @get("hello/:name")
        async def hello_name(self, name: str) -> dict:
            greeting = self.greeter.greet(name)
            await self.repository.save_greeting(greeting, datetime.now())
            return {"greeting": greeting}
    ```

## Using backgound taks

The greetings are being save to the database, but now we have a problem: the
user has to wait until the greeting is saved before receiving it.

To solve this problem and improve the user experience, we can use *background tasks*:

=== "application/controller.py"

    ```python
    from datetime import datetime
    from selva.di import Inject
    from selva.web import RequestContext, controller, get
    from selva.web.responses import JSONResponse, BackgroundTask
    from .repository import GreetingRepository
    from .service import Greeter
    
    
    @controller
    class GreetingController:
        greeter: Greeter = Inject()
        repository: GreetingRepository = Inject()
    
        @get("hello/:name")
        async def hello_name(self, name: str, context: RequestContext) -> JSONResponse:
            greeting = self.greeter.greet(name)

            background = BackgroundTask(
                self.repository.save_greeting,
                greeting,
                datetime.now(),
            )

            return JSONResponse(
                {"greeting": greeting},
                background=background,
            )
    ```

    1.  We called the method `add_delayed_task` from `RequestContext` to schedule
        a function to be called after the response is completed, thus avoiding
        having to wait for the message to be saved before sending the response

## Retrieving the greeting logs

To see the greetings saved to the database, we just need to add a route to get
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

=== "application/controllers.py"

    ```python
    @controller
    class GreetingController:
        # ...
        @get("/logs")
        async def greeting_logs(self) -> list[tuple[str, str]]:
            return await self.repository.get_greetings()
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
        "datetime": "2022-07-06 14:23:14"
    },
    {
        "greeting": "Hello, Python!",
        "datetime": "2022-07-06 14:23:08"
    },
]
```
