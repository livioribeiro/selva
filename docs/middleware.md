# Middleware

The middleware pipeline is configured with the `MIDDLEWARE` configuration property. It must contain a list of classes
that inherit from `selva.web.middleware.Middleware`.

The `Middleware` base class defines the property `app` that should be called in order to invoke the next middleware,
similar to what a pure asgi middleware would look like.

## Usage

To demonstrate the middleware system, we will create a timing middleware that will output to the console the time spent
in the processing of the request:

=== "application/controller.py"

    ```python
    from selva.web import controller, get
    
    
    @controller
    class HelloController:
        @get
        def hello(self) -> dict:
            return {"greeting": "Hello, World!"}
    ```

=== "application/middleware.py"

    ```python
    from datetime import datetime
    
    from selva.web.context import RequestContext
    from selva.web.middleware import Middleware
    
    
    class TimingMiddleware(Middleware):
        async def __call__(self, context: RequestContext):
            request_start = datetime.now()
            response = await self.app(context) # (1)
            request_end = datetime.now()
    
            delta = request_end - request_start
            print(f"Request time: {delta}")
    
            return response
    ```

    1. Invoke application to obtain response

=== "configuration/settings.py"

    ```python
    from application.middleware import TimingMiddleware
    
    MIDDLEWARE = [
        TimingMiddleware,
    ]
    ```

## Middleware dependencies

Middleware instances are created using the same machinery as services, and therefore can have services of their own. Our
`TimingMiddleware`, for instance, could persist the timings using a service instead of printing to the console:

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
    
    from selva.di import Inject
    from selva.web.context import RequestContext
    from selva.web.middleware import Middleware
    
    from application.service import TimingService
    
    
    class TimingMiddleware(Middleware):
        timing_service: TimingService = Inject()
    
        async def __call__(self, context: RequestContext):
            request_start = datetime.now()
            response = await self.app(context)
            request_end = datetime.now()
    
            await self.timing_service.save(request_start, request_end)
    
            return response
    ```