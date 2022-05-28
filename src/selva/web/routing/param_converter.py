from selva.di.decorators import singleton

from .converters import PathParameterConverter


@singleton(provides=PathParameterConverter[int])
class IntPathParamConverter(PathParameterConverter[int]):
    async def from_path(self, value: str) -> int:
        return int(value)

    async def to_path(self, obj: int) -> str:
        return str(obj)


@singleton(provides=PathParameterConverter[float])
class FloatPathParamConverter(PathParameterConverter[float]):
    async def from_path(self, value: str) -> float:
        return float(value)

    async def to_path(self, obj: float) -> str:
        return str(obj)


@singleton(provides=PathParameterConverter[str])
class StrPathParamConverter(PathParameterConverter[str]):
    async def from_path(self, value: str) -> str:
        return value

    async def to_path(self, obj: str) -> str:
        return obj


@singleton(provides=PathParameterConverter[bool])
class BoolPathParamConverter(PathParameterConverter[bool]):
    async def from_path(self, value: str) -> bool:
        return value in ["1", "true", "True"]

    async def to_path(self, obj: bool) -> str:
        return str(obj)
