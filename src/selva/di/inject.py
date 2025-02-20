from typing import Annotated, NamedTuple, Self, TypeVar

T = TypeVar("T")


class Inject:
    """Defines a service dependency"""

    def __init__(self, name: str):
        self.name = name

    def __class_getitem__(cls, item: str) -> Self:
        if not isinstance(item, str):
            raise TypeError()

        return Inject(name=item)
