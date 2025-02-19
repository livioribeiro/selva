# Project Selva

Documentation: https://livioribeiro.github.io/selva/

Selva is a Python ASGI web framework built on top of [asgikit](https://pypi.org/project/asgikit/)
and inspired by Spring Boot, AspNet, FastAPI and Go's net/http.

It features a Dependency Injection system to help build robust and reliable applications.

## Quick start

Install `selva` and `uvicorn` to run application:

```shell
pip install selva uvicorn[standard]
```

Create a module called `application.py`:

```shell
touch application.py
```

Create a handler:

```python
from selva.web import Request, get


@get
async def hello(request: Request):
    await request.respond("Hello, World!")
```

Run application with `uvicorn` (Selva will automatically load `application.py`):

```shell
uvicorn selva.run:app --reload
```
