# Middleware

A linha de pipeline é configurada com a propriedade de configuração `middleware`.
Ela deve conter uma lista de funções que recebem a próxima aplicação na linha, o
objeto de configurações e o contêiner de injeção de dependências e deve retornar
uma instância de middleware asgi.

```python
def middleware_factory(app, settings, di):
    async def inner(scope, receive, send):
        await app(scope, receive, send)

    return inner
```

Qualquer middleware asgi pode ser usado na linha de middleware. Por exemplo, é possível
utilizar o SessionMiddleware do starlette:


=== "application/middleware.py"

    ```python
    from starlette.middleware.sessions import SessionMiddleware
    
    
    def session_middleware(app, settings, di):
        return SessionMiddleware(app, secret_key=settings.session.secret_key)
    ```

=== "configuration/settings.yaml"

    ```yaml
    middleware:
      - application.middleware:session_middleware

    session:
      secret_key: super_secret_key
    ```

## Utilização

Para demonstrar o systema de middleware, nós criaremos um middleware temporizador
que exibirá no console o tempo gasto no processamento da requisição::

=== "application/handler.py"

    ```python
    from asgikit.requests import Request
    from asgikit.responses import respond_json
    from selva.web import get
    
    
    @get
    async def hello(request: Request):
        await respond_json(request.response, {"greeting": "Hello, World!"})
    ```

=== "application/middleware.py"

    ```python
    from collections.abc import Callable
    from datetime import datetime
    
    import structlog
    
    from selva.di import service
    
    logger = structlog.get_logger()
    
    
    def timing_middleware(app, settings, di):
        async def inner(scope, receive, send):
            request_start = datetime.now()
            await app(scope, receive, send)
            request_end = datetime.now()

            delta = request_end - request_start
            logger.info("request duration", duration=str(delta))
        return inner
    ```

=== "configuration/settings.yaml"

    ```yaml
    middleware:
      - application.middleware.timing_middleware
    ```

## Dependências do middleware

Funções de middleware pode usar o contêiner de injeção de dependências para recuperar
serviços que o middleware possa precisar. Nós podemos reescrever o middleware temporizador
para persistir os tempos usando um serviço ao invés de exibir no console:

=== "application/middleware.py"

    ```python
    from datetime import datetime
    
    from application.service import TimingService
    
    
    class TimingMiddleware:
        def __init__(self, app, timing_service: TimingService):
            self.timing_service = timing_service

        async def __call__(self, scope, receive, send):
            request_start = datetime.now()
            await app(scope, receive, send)
            request_end = datetime.now()

            await self.timing_service.save(request_start, request_end)


    async def timing_middleware(app, settings, di):
        timing_service = await di.get(TimingService)
        return TimingMiddleware(app, timing_service)
    ```

=== "application/service.py"

    ```python
    from datetime import datetime
    
    from selva.di import service
    
    @service
    class TimingService:
        async def save(start: datetime, end: datetime):
            ...
    ```