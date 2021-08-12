from abc import ABC, abstractmethod

from dependency_injector import singleton


class Interface(ABC):
    @abstractmethod
    def method(self):
        raise NotImplementedError()


class Implementation(Interface):
    def method(self):
        pass


@singleton
async def service_factory() -> Interface:
    return Implementation()
