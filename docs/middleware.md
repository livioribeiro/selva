# Middleware

The middleware pipeline is configured with the `MIDDLEWARE` configuration property. It must contain a list of classes
that inherit from `selva.web.middleware.Middleware`.

## Usage

To demonstrate the middleware system, we will create a timing middleware that will output to the console the time spent
in the processing of the request:

=== "application/controller.py"

    ```python
    from asgikit.requests import Request
    from asgikit.responses import respond_json
    from selva.web import controller, get
    
    
    @controller
    class HelloController:
        @get
        async def hello(self, request: Request):
            await respond_json(request.response, {"greeting": "Hello, World!"})
    ```

=== "application/middleware.py"

    ```python
    from collections.abc import Callable
    from datetime import datetime
    
    from asgikit.requests import Request
    from selva.web.middleware import Middleware
    from loguru import logger
    
    
    class TimingMiddleware(Middleware):
        async def __call__(self, chain: Callable, request: Request):
            request_start = datetime.now()
            await chain(request) # (1)
            request_end = datetime.now()
    
            delta = request_end - request_start
            logger.info("Request time: {}", delta)
    ```

    1. Invoke the middleware chain to process the request

=== "configuration/settings.yaml"

    ```yaml
    middleware:
      - application.middleware.TimingMiddleware
    ```

## Middleware dependencies

Middleware instances are created using the same machinery as services, and therefore
can have services of their own. Our `TimingMiddleware`, for instance, could persist
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
    from collections.abc import Callable
    from datetime import datetime
    
    from asgikit.requests import Request
    from selva.di import Inject
    from selva.web.middleware import Middleware
    
    from application.service import TimingService
    
    
    class TimingMiddleware(Middleware):
        timing_service: TimingService = Inject()
    
        async def __call__(self, chain: Callable, request: Request):
            request_start = datetime.now()
            await chain(request)
            request_end = datetime.now()
    
            await self.timing_service.save(request_start, request_end)
    ```