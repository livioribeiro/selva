# Startup hooks

Selva provides decorators to mark functions as hooks that will be called when the
application starts. The functions will be called in the order they are discovered
and if any of them raise en error, the application will not start.

```python
from selva.web import startup


@startup
def my_startup_hook():
    ...
```

Startup functions can receive services as parameters through the dependency injection
system.

```python
from selva.di import service
from selva.web import startup


@service
class OIDCService:
    async def oidc_discovey(self):
        ...


@startup
async def my_startup_hook(oidc_service: OIDCService):
    await oidc_service.oidc_discovey()
```

You can use the `Inject` annotation if you need a named service.

```python
from typing import Annotated

from selva.di import Inject, service
from selva.web import startup


@service(name="provider")
class OIDCService:
    async def oidc_discovey(self):
        ...


@startup
async def my_startup_hook(oidc_service: Annotated[OIDCService, Inject(name="provider")]):
    await oidc_service.oidc_discovey()
```