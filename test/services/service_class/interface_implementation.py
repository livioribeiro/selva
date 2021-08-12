from abc import ABC, abstractmethod

from dependency_injector import singleton


class Interface(ABC):
    @abstractmethod
    def method(self):
        raise NotImplementedError()


@singleton(provides=Interface)
class Implementation(Interface):
    def method(self):
        pass
