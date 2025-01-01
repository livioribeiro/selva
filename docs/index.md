# Selva

Selva is a tool for creating ASGI applications that are easy to build and maintain.

It is built on top of [asgikit](https://pypi.org/project/asgikit/) and comes with
a dependency injection system built upon Python type annotations. It is compatible with python 3.11+.

## Quickstart

Install `selva` and `uvicorn`:

```shell
pip install selva uvicorn[standard]
```

Create file `application.py`:

```python
from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import get


@get
async def hello(request: Request):
    await respond_text(request.response, "Hello, World")
```

Run application with `uvicorn`. Selva will automatically load `application.py`:

```shell
uvicorn selva.run:app
```

```
INFO:     Started server process [1000]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
