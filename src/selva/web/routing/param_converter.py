from selva.di import service

from .converter import PathParamConverter


@service(provides=PathParamConverter[int])
class IntPathParamConverter(PathParamConverter[int]):
    async def from_path(self, value: str) -> int:
        return int(value)

    async def to_path(self, obj: int) -> str:
        return str(obj)


@service(provides=PathParamConverter[float])
class FloatPathParamConverter(PathParamConverter[float]):
    async def from_path(self, value: str) -> float:
        return float(value)

    async def to_path(self, obj: float) -> str:
        return str(obj)


@service(provides=PathParamConverter[str])
class StrPathParamConverter(PathParamConverter[str]):
    async def from_path(self, value: str) -> str:
        return value

    async def to_path(self, obj: str) -> str:
        return obj


@service(provides=PathParamConverter[bool])
class BoolPathParamConverter(PathParamConverter[bool]):
    async def from_path(self, value: str) -> bool:
        return value in ["1", "true", "True"]

    async def to_path(self, obj: bool) -> str:
        return str(obj)
