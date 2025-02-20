# Services

Services are types registered with the dependency injection container that can be
injected in other services and handlers. They are defined with the decorator `@service`.

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

## Service classes

Services defined as classes have dependencies as class annotations.

```python
from typing import Annotated
from selva.di import Inject, service


@service
class MyService:
    pass


@service
class OtherService:
    property: Annotated[MyService, Inject]
```

When the service type is requested in the dependency injection container, the class
will be inspected for the annotated dependencies that will be created and then injected
into the requested service.

Annotations without `Inject` will be ignored.

### Initializers and finalizers

Optionally, service classes can define two methods: `initialize()`, that will be
called after service creation and dependency injection; and `finalize()`, that will
be called on application shutdown.

```python
from selva.di import service


@service
class MyService:
    async def initialize(self):
        """perform initialization logic"""

    async def finalize(self):
        """perform finalization logic"""
```

The `initialize()` and `finalize()` methods do not need to be async.

### Services providing an interface

You can have services that provide an interface instead of their own type, so we
request the interface as dependency instead of the concrete type.

```python
from typing import Annotated

from selva.di import Inject, service


class Interface:
    def some_method(self): pass


@service(provides=Interface)
class MyService:
    def some_method(self): pass


@service
class OtherService:
    dependency: Annotated[Interface, Inject]
```

When `OtherService` is created, the dependency injection container look for a service
of type `Interface` and will produce an instance of the `MyService` class.

### Named services

Services can be registered with a name, so you can have more than one service of
the same type, given they have distinct names. Without a name, a service is registered
as the default for that type.

```python
from typing import Annotated

from selva.di import Inject, service


class Interface: pass


@service(name="A", provides=Interface)
class ServiceA: pass


@service(name="B", provides=Interface)
class ServiceB: pass


@service
class OtherService:
    dependency_a: Annotated[Interface, Inject("A")]
    dependency_b: Annotated[Interface, Inject("B")]
```

### Optional dependencies

If a requested dependency is not registered, an error is raised, unless there is
a default value declared, in the case the property will have that value when the
service is created.

```python
from typing import Annotated

from selva.di import Inject, service


@service
class SomeService:
    pass


@service
class MyService:
    dependency: Annotated[SomeService, Inject] = None

    def some_method(self):
        if self.dependency:
            ...
```

## Services as factory functions

In order to register a type that we do not own, for example, a type from an external
library, we can use a factory function:

```python
from selva.di import service
from some_library import SomeClass


@service
async def some_class_factory() -> SomeClass:
    return SomeClass()
```

The return type annotation is required in factory functions, as that will be the
service provided by function. If the return type annotation is not provided, an
error is raised.

The value of the parameter `provides` in `@service` is ignored when decorating a
factory function, and a warning will be raised.

Factory function parameters do not need the `Inject` annotation, unless they need
to specify a named dependency:

```python
from typing import Annotated

from selva.di import Inject, service
from some_library import SomeClass


@service
async def some_class_factory(
    dependency: MyService,
    other: Annotated[OtherService, Inject("service_name")]
) -> SomeClass:
    return SomeClass()
```

### Initialization and finalization

To perform initialization on factory functions, you just execute the logic before
returning the service.

```python
from selva.di import service


class SomeClass:
    pass


@service
async def factory() -> SomeClass:
    some_service = SomeClass()
    # perform initialization login
    return some_service
```

To perform finalization, you use the `yield` instead of `return` and execute the
finalization logic afterward.

```python
from selva.di import service


class SomeClass:
    pass


@service
async def factory() -> SomeClass:
    some_service = SomeClass()
    # perform initialization logic
    yield some_service
    # perform finalization logic
```

### Named services

Named services work the same as in service classes.

```python
from typing import Annotated

from selva.di import Inject, service

from some_library import SomeClass


@service(name="service_name")
def factory() -> SomeClass:
    return SomeClass


@service
class MyService:
    dependency: Annotated[SomeClass, Inject("service_name")]
```

### Optional dependencies

Optional dependencies work the same as in service classes, in that you specify a
default value for the argument.

```python
from typing import Annotated

from selva.di import Inject, service
from some_library import SomeClass


@service
async def some_class_factory(
    dependency: MyService,
    other: Annotated[OtherService, Inject("service_name")] = None
) -> SomeClass:
    if other:
        ...

    return SomeClass()
```
