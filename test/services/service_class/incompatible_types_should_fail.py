from abc import ABC, abstractmethod

from dependency_injector import singleton


class Interface(ABC):
    @abstractmethod
    def method(self):
        pass


@singleton(provides=Interface)
class Implementation:
    def method(self):
        pass
