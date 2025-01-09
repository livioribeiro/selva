# Services

Services are types registered with the dependency injection container that can be
injected in other services and handlers.

They can be defined as classes or functions decorated with `@service`. Classes have
dependencies as annotations while functions have dependencies as parameters.

```python
from typing import Annotated
from selva.di import Inject, service


@service
class MyService:
    pass


@service
class MyOtherService:
    dependency: Annotated[MyService, Inject]


class SomeClass:
    pass


class OtherClass:
    def __init__(self, dependency: SomeClass):
        self.dependency = dependency


@service
async def factory() -> SomeClass:
    return SomeClass()


@service
async def other_factory(dependency: SomeClass) -> OtherClass:
    return OtherClass(dependency)
```