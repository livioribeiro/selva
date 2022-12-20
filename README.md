# Project Selva

Documentation: https://livioribeiro.github.io/selva/

Selva is a Python ASGI web framework built on top of [starlette](https://www.starlette.io/)
and inspired by Spring Boot, AspNet Core and FastAPI.

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

Create a controller:

```python
from selva.web import controller, get


@controller
class Controller:
    @get
    def hello(self):
        return "Hello, World!"
```

Run application with `uvicorn` (Selva will automatically load `application.py`):

```shell
uvicorn selva.run:app --reload
```
