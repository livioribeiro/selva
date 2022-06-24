import inspect
from typing import Annotated


class Named:
    def __init__(self):
        raise TypeError("Cannot instantiate Named")

    def __class_getitem__(cls, item: tuple[type, str]):
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("Named[...] requires 2 arguments")

        service, name = item

        if not inspect.isclass(service):
            raise ValueError(
                "Invalid argument for Named[...]. First argument must be a class"
            )

        if not isinstance(name, str):
            raise ValueError(
                "Invalid argument for Named[...]. Second argument must be str"
            )

        return Annotated[service, name]
