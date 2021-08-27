from typing import Generic, TypeVar

from dependency_injector import singleton

T = TypeVar("T")


class Interface(Generic[T]):
    pass


@singleton(provides=Interface[int])
class Implementation(Interface[int]):
    pass
