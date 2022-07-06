from .converter import path_param_converter


@path_param_converter(int)
class IntPathParamConverter:
    async def from_path(self, value: str) -> int:
        return int(value)

    async def to_path(self, obj: int) -> str:
        return str(obj)


@path_param_converter(float)
class FloatPathParamConverter:
    async def from_path(self, value: str) -> float:
        return float(value)

    async def to_path(self, obj: float) -> str:
        return str(obj)


@path_param_converter(str)
class StrPathParamConverter:
    async def from_path(self, value: str) -> str:
        return value

    async def to_path(self, obj: str) -> str:
        return obj


@path_param_converter(bool)
class BoolPathParamConverter:
    async def from_path(self, value: str) -> bool:
        return value in ["1", "true", "True"]

    async def to_path(self, obj: bool) -> str:
        return str(obj)
