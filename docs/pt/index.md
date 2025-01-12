# Selva

Selva é uma ferramenta para criar aplicações ASGI que são fáceis de construir e manter.

É baseado na biblioteca [asgikit](https://pypi.org/project/asgikit/) e tem um sistema
de injeção de dependência através de anotações de tipo do Python.
É compatível com Python 3.11+.

## Começando

Instale `selva` e `uvicorn`:

```shell
pip install selva uvicorn[standard]
```

Crie o arquivo `application.py`:

```python
from asgikit.requests import Request
from asgikit.responses import respond_text
from selva.web import get


@get
async def hello(request: Request):
    await respond_text(request.response, "Hello, World")
```

Execute a aplicação with `uvicorn`. Selva vai carregar automaticamente o `application.py`:

```shell
uvicorn selva.run:app
```

```
INFO:     Started server process [1000]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
