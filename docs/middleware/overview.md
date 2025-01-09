# Middleware

The middleware pipeline is configured with the `middleware` configuration property.
It must contain a list of functions that have the following signature:

```python
async def middleware(callnext, request): ...
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
    
    
    async def timing_middleware(callnext, request):
        request_start = datetime.now()
        await callnext(request) # (1)
        request_end = datetime.now()

        delta = request_end - request_start
        logger.info("request duration", duration=str(delta))
    ```

    1. Invoke the middleware chain to process the request

=== "configuration/settings.yaml"

    ```yaml
    middleware:
      - application.middleware.timing_middleware
    ```

## Middleware dependencies

Middleware functions are called using the same machinery as handlers, and therefore
can have services injected. Our `timing_middleware`, for instance, could persist
the timings using a service instead of printing to the console:

=== "application/service.py"

    ```python
    from datetime import datetime
    
    from selva.di import service
    
    @service
    class TimingService:
        async def save(start: datetime, end: datetime):
            ...
    ```

=== "application/middleware.py"

    ```python
    from datetime import datetime
    from typing import Annotated
    
    from selva.di import service, Inject
    
    from application.service import TimingService
    
    
    async def __call__(
        call_next, request,
        timing_service: Annotated[TimingService, Inject]
    ):
        request_start = datetime.now()
        await call_next(request)
        request_end = datetime.now()

        await timing_service.save(request_start, request_end)
    ```