# Project Selva

Selva is a Python ASGI web framework built on top of [asgikit](https://github.com/livioribeiro/asgikit)
and inspired by Spring Boot, AspNet Core and FastAPI.

## Installation

```shell
pip install selva
```

## Usage

Create an application and controller

```python
from selva.web import Application, controller, get


@controller
class Controller:
    @get
    def hello(self):
        return "Hello, World!"


app = Application(Controller)
```

Add a service

```python
from selva.di import service
from selva.web import Application, controller, get


@service
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


@controller
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get
    def hello(self):
        return self.greeter.greet("World")


app = Application(Controller, Greeter)
```

Get parameters from path

```python
from selva.di import service
from selva.web import Application, controller, get


@service
class Greeter:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


@controller
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get("hello/{name}")
    def hello(self, name: str):
        greeting = self.greeter.greet(name)
        # A json response will be created from the returned dict
        return {"greeting": greeting}


app = Application(Controller, Greeter)
```

Configurations with [Pydantic](https://pydantic-docs.helpmanual.io/usage/settings/)

```python
from selva.di import service
from selva.web import Application, RequestContext, controller, get
from pydantic import BaseSettings


class Settings(BaseSettings):
    DEFAULT_NAME = "World"


@service
def settings_factory() -> Settings:
    return Settings()


@service
class Greeter:
    def __init__(self, settings: Settings):
        self.default_name = settings.DEFAULT_NAME

    def greet(self, name: str | None) -> str:
        name = name or self.default_name
        return f"Hello, {name}!"


@controller
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get("hello/{name}")
    def hello(self, name: str):
        greeting = self.greeter.greet(name)
        return {"greeting": greeting}

    @get("hello")
    def hello_optional(self, context: RequestContext):
        name = context.query.get("name")
        greeting = self.greeter.greet(name)
        return {"greeting": greeting}


app = Application(Controller, Greeter, settings_factory)
```

Manage services lifecycle (e.g [Databases](https://www.encode.io/databases/))

```python
from selva.di import service, initializer, finalizer
from selva.web import Application, RequestContext, controller, get
from pydantic import BaseSettings, PostgresDsn
from databases import Database


class Settings(BaseSettings):
    DEFAULT_NAME = "World"
    DATABASE_URL: PostgresDsn


@service
def settings_factory() -> Settings:
    return Settings()


@service
class Repository:
    def __init__(self, settings: Settings):
        self.database = Database(settings.DATABASE_URL)

    async def get_greeting(self, name: str) -> str:
        result = await self.database.fetch_one(
            query="select text from greeting where name = :name",
            values={"name": name}
        )

        return result.text

    @initializer
    async def initialize(self):
        await self.database.connect()
        print("Database connection opened")

    @finalizer
    async def finalize(self):
        await self.database.disconnect()
        print("Database connection closed")


@service
class Greeter:
    def __init__(self, repository: Repository, settings: Settings):
        self.repository = repository
        self.default_name = settings.DEFAULT_NAME

    async def greet(self, name: str | None) -> str:
        name = name or self.default_name
        return await self.repository.get_greeting(name)


@controller
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get("hello/{name}")
    def hello(self, name: str):
        greeting = self.greeter.greet(name)
        return {"greeting": greeting}

    @get("hello")
    def hello_optional(self, context: RequestContext):
        name = context.query.get("name")
        greeting = self.greeter.greet(name)
        return {"greeting": greeting}


app = Application(Controller, Greeter, Repository, settings_factory)
```

Define controllers and services in a separate module

```
├───application
│   ├───controllers.py
│   ├───repository.py
│   ├───services.py
│   └───settings.py
└───main.py
```

```python
### application/settings.py
from selva.di import service
from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    DEFAULT_NAME = "World"
    DATABASE_URL: PostgresDsn


@service
def settings_factory() -> Settings:
    return Settings()
```

```python
### application/repository.py
from selva.di import service, initializer, finalizer
from databases import Database
from .settings import Settings

@service
class Repository:
    def __init__(self, settings: Settings):
        self.database = Database(settings.DATABASE_URL)

    async def get_greeting(self, name: str) -> str:
        result = await self.database.fetch_one(
            query="select text from greeting where name = :name",
            values={"name": name}
        )

        return result.text

    @initializer
    async def initialize(self):
        await self.database.connect()
        print("Database connection opened")

    @finalizer
    async def finalize(self):
        await self.database.disconnect()
        print("Database connection closed")
```

```python
### application/services.py
from selva.di import service
from .settings import Settings
from .repository import Repository


@service
class Greeter:
    def __init__(self, repository: Repository, settings: Settings):
        self.repository = repository
        self.default_name = settings.DEFAULT_NAME

    async def greet(self, name: str | None) -> str:
        name = name or self.default_name
        return await self.repository.get_greeting(name)
```

```python
### application/controllers.py
from selva.web import RequestContext, controller, get
from .services import Greeter

@controller
class Controller:
    def __init__(self, greeter: Greeter):
        self.greeter = greeter

    @get("hello/{name}")
    def hello(self, name: str):
        greeting = self.greeter.greet(name)
        return {"greeting": greeting}

    @get("hello")
    def hello_optional(self, context: RequestContext):
        name = context.query.get("name")
        greeting = self.greeter.greet(name)
        return {"greeting": greeting}
```

```python
### main.py
from selva.web import Application


# module named "application" is automatically registered
app = Application()
```

Websockets

```python
from pathlib import Path
from selva.web import Application, FileResponse, RequestContext, controller, get, websocket
from selva.web.errors import WebSocketDisconnectError

@controller
class WebSocketController:
    @get
    def index(self) -> FileResponse:
        return FileResponse(Path(__file__).parent / "index.html")

    @websocket("/chat")
    async def chat(self, context: RequestContext):
        client = context.websocket

        await client.accept()
        print(f"[open] Client connected")

        self.handler.clients.append(client)

        while True:
            try:
                message = await client.receive()
                print(f"[message] {message}")
                await client.send_text(message)
            except WebSocketDisconnectError:
                print("[close] Client disconnected")
                break


app = Application(WebSocketController)
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WebSocket chat</title>
</head>
<body>
<form id="chat-form">
    <textarea name="message-list" id="message-list" cols="30" rows="10" readonly></textarea>
    <p>
        <input type="text" name="message-box" id="message-box" />
        <button type="submit">Send</button>
    </p>
</form>

<script>
    const messages = [];

    const chat = document.getElementById("chat-form");
    const textarea = document.getElementById("message-list");
    textarea.value = "";
    const messageInput = document.getElementById("message-box");

    const socket = new WebSocket("ws://localhost:8000/chat");

    function addMessage(message) {
        messages.push(message)
        textarea.value = `${messages.join("\n")}`;
        textarea.scrollTop = textarea.scrollHeight;
    }

    chat.onsubmit = (event) => {
        event.preventDefault();
        const message = messageInput.value;
        socket.send(message);
        messageInput.value = "";
    };

    socket.onopen = (event) => {
        console.log("[open] Client connected");
    };

    socket.onmessage = (event) => {
        const message = event.data;
        console.log(`[message] "${message}"`)
        addMessage(message);
    };

    socket.onclose = (event) => {
        if (event.wasClean) {
            console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
        } else {
            console.log('[close] Connection died');
        }
    };

    socket.onerror = function(error) {
        console.log(`[error] ${error.message}`);
    };
</script>
</body>
</html>
```
