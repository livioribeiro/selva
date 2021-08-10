# Dependency Injector

Yet another dependency injection library for Python

Usage:

```python
from abc import ABC, abstractmethod
from dependency_injector import Container

ioc = Container()


# Register a service
@ioc.singleton
class Service1:
    pass


# Register a service with dependency
@ioc.singleton
class Service2:
    def __init__(self, service1: Service1):
        self.service1 = service1


# Get an instance of Service2
service2 = ioc.get(Service2)
assert isinstance(service2.service1, Service1)


# Using factory functions
@ioc.singleton
def service1_factory() -> Service1:
    return Service1()


@ioc.singleton
def service2_factory(service1: Service1) -> Service2:
    return Service2(service1)


# Interface with implementation
class Interface(ABC):
    @abstractmethod
    def method(self):
        pass


@ioc.singleton(provides=Interface)
class Implementation(Interface):
    def method(self):
        pass


# Get service implementing Interface
service = ioc.get(Interface)
assert isinstance(service, Implementation)


# Using factory function
@ioc.singleton
def factory_function() -> Interface:
    return Implementation()


# Register transient services
@ioc.transient
class TransientService:
    pass


instance1 = ioc.get(TransientService)
instance2 = ioc.get(TransientService)

# A new instance will be returned every time it is requested
assert id(instance1) != id(instance2)


# Register context dependent services
@ioc.dependent
class DependentService:
    pass


# Define a context object
class MyContext:
    pass


context_obj = MyContext()

# Get the service bound by the context
dependent_instance1 = ioc.get(DependentService, context=context_obj)
dependent_instance2 = ioc.get(DependentService, context=context_obj)

# The same instance will be returned for a given context
assert id(dependent_instance1) == id(dependent_instance2)


# Call function with dependencies
def function(service1: Service1):
    pass


ioc.call(function)


# Function with additional parameters
def function_with_params(service1: Service1, parameter: int):
    pass


ioc.call(function, kwargs={"parameter": 1})

```