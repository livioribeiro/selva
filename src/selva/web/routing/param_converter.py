from selva.di import service

from .converter import PathParameterConverter


@service(provides=PathParameterConverter[int])
class IntPathParamConverter(PathParameterConverter[int]):
    async def from_path(self, value: str) -> int:
        return int(value)

    async def to_path(self, obj: int) -> str:
        return str(obj)


@service(provides=PathParameterConverter[float])
class FloatPathParamConverter(PathParameterConverter[float]):
    async def from_path(self, value: str) -> float:
        return float(value)

    async def to_path(self, obj: float) -> str:
        return str(obj)


@service(provides=PathParameterConverter[str])
class StrPathParamConverter(PathParameterConverter[str]):
    async def from_path(self, value: str) -> str:
        return value

    async def to_path(self, obj: str) -> str:
        return obj


@service(provides=PathParameterConverter[bool])
class BoolPathParamConverter(PathParameterConverter[bool]):
    async def from_path(self, value: str) -> bool:
        return value in ["1", "true", "True"]

    async def to_path(self, obj: bool) -> str:
        return str(obj)
