from typing import Generic, TypeVar

from selva.di import service

T = TypeVar("T")


class Interface(Generic[T]):
    pass


@service(provides=Interface[int])
class Implementation(Interface[int]):
    pass
