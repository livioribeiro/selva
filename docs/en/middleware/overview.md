# Middleware

The middleware pipeline is configured with the `middleware` configuration property.
It must contain a list of functions that receive the next app in the pipeline, the
settings object and the dependency injection container and must return a plain asgi
middleware instance:

```python
def middleware_factory(app, settings, di): ...
```

Any asgi middleware can be used in the middleware pipeline. For instance, it is
possible to use the SessionMiddleware from starlette:


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

## Usage

To demonstrate the middleware system, we will create a timing middleware that will
output to the console the time spent in the processing of the request:

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

## Middleware dependencies

Middleware functions can use the provided dependency injection container to get
services the middleware might need. We could rewrite the timing middleware to persist
the timings using a service instead of printing to the console:

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