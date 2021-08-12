# Dependency Injector

Yet another dependency injection library for Python

## Usage

Declare services
```python
### app/services.py

from dependency_injector import singleton


# Register a service
@singleton
class Service1:
    pass


# Register a service with dependency
@singleton
class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1
```

You can also use factory functions

```python
### app/services.py

from dataclasses import dataclass
from dependency_injector import singleton

class Service1:
    pass


# works with dataclasses too
@dataclass
class Service2:
    service1: Service1


@singleton
def service1_factory() -> Service1:
    return Service1()


@singleton
def service2_factory(service1: Service1) -> Service2:
    return Service2(service1)
```

Requesting the services

```python
### app/main.py

from depedency_injector import Container
from app.services import Service1, Service2


async def main():
    # Create an ioc container
    ioc = Container()

    # Tell container to scan package for services
    ioc.scan_packages("app.services")

    # also works with module instances
    from app import services
    ioc.scan_packages(services)

    # Get an instance of Service2
    service2 = await ioc.get(Service2)
    assert isinstance(service2.service1, Service1)
```

There is also a sync container

```python
### app/main.py

from depedency_injector import SyncContainer
from app.services import Service1, Service2

ioc = SyncContainer()

ioc.scan_packages("app.services")

service2 = ioc.get(Service2)
assert isinstance(service2.service1, Service1)
```

Interface with implementation

```python
### app/services.py

from abc import ABC, abstractmethod
from dependency_injector import singleton

class Interface(ABC):
    @abstractmethod
    def method(self):
        raise NotImpementedError()


@singleton(provides=Interface)
class Implementation(Interface):
    def method(self):
        pass


# with factory function
@singleton
def factory_function() -> Interface:
    return Implementation()


### app/main.py

from dependency_injector import Container
from app.services import Interface, Implementation


async def main():
    ioc = Container()
    ioc.scan_packages("app.services")
    service = ioc.get(Interface)
    assert isinstance(service, Implementation)
```

Register services directly with the container

```python
from dependency_injector import Container, Scope


class Service:
    pass


async def main():
    ioc = Container()
    ioc.register(Service, Scope.SINGLETON)

    service = await ioc.get(Service)
    assert isinstance(service, Service)


# with interface and implementation
class Interface:
    pass


class Implementation(Interface):
    pass

async def main():
    ioc.register(Implementation, Scope.SINGLETON, provides=Interface)

    service = await ioc.get(Interface)
    assert isinstance(service, Implementation)

```

Transient services

```python
### app/services.py

from dependency_injector import transient

@transient
class TransientService:
    pass


### app.main.py

import asyncio
from dependency_injector import Container
from app.services import TransientService


async def main():
    ioc = Container()
    ioc.scan_packages("app.services")

    instance1 = await ioc.get(TransientService)
    instance2 = await ioc.get(TransientService)

    # A new instance will be returned every time it is requested
    assert instance1 is not instance2
```

Context dependent services

The same object is return for a given context object. One example of aplication of dependent services is on a web server that returns the same database connection for a given request.

```python
### app/services.py

from dependency_injector import dependent


@dependent
class DependentService:
    pass


### app/main.py

from dependency_injector import Container
from app.services import DependentService

# Define a context object
class MyContext:
    pass


async def main():
    ioc = Container()
    ioc.scan_packages("app.services")

    context1 = MyContext()

    # Get the service bound by the context
    dependent_instance1 = await ioc.get(DependentService, context=context1)
    dependent_instance2 = await ioc.get(DependentService, context=context1)

    # The same instance will be returned for a given context
    assert dependent_instance1 is dependent_instance2

    # with a different context
    context2 = MyContext()
    dependent_instance3 = await ioc.get(DependentService, context=context2)
    assert dependent_instance3 is dependent_instance1
    assert dependent_instance3 is dependent_instance2
```

Call function with dependencies

```python

def function(service1: Service1):
    pass


ioc.call(function)


# Function with additional parameters
def function_with_params(service1: Service1, parameter: int):
    pass


ioc.call(function, kwargs={"parameter": 1})

```