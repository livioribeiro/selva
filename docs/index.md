# Selva

Selva is a tool for creating ASGI applications that are easy to build and maintain.

It is based on Starlette and Pydantic and comes with a dependency injection system built upon Python type annotations.

## Quickstart

Install `selva` and `uvicorn`:

```shell
pip install selva uvicorn
```

Create file `application.py`:

```python
from selva.web import controller, get


@controller
class Controller:
    @get
    def hello(self):
        return "Hello, World"
```

Run application with `uvicorn`. Selva will automatically load `application.py`:

```shell
uvicorn selva.run:app
```

```
INFO:     Started server process [18664]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
