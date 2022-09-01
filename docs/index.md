# Selva

Selva is a tool for creating ASGI applications that are easy to build and maintain.

It comes with a dependency injection system built upon Python type annotations.

## Quickstart

Install `selva` and `uvicorn`:

```shell
pip install selva uvicorn
```

Create file `main.py`:

```python
from selva.web import Selva, controller, get


@controller
class Controller:
    @get
    def hello(self):
        return "Hello, World"


app = Selva(Controller)
```

Run application with `uvicorn`:

```shell
uvicorn main:app
```

```
INFO:     Started server process [18664]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
