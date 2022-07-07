from selva.web.errors import NotFoundError

from .converter import path_param_converter


@path_param_converter(str)
class StrPathParamConverter:
    async def from_path(self, value: str) -> str:
        return value

    async def to_path(self, obj: str) -> str:
        return obj


@path_param_converter(int)
class IntPathParamConverter:
    async def from_path(self, value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            raise NotFoundError()

    async def to_path(self, obj: int) -> str:
        return str(obj)


@path_param_converter(float)
class FloatPathParamConverter:
    async def from_path(self, value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            raise NotFoundError()

    async def to_path(self, obj: float) -> str:
        return str(obj)


@path_param_converter(bool)
class BoolPathParamConverter:
    TRUE_VALUES = ["1", "true", "True", "TRUE"]
    FALSE_VALUES = ["0", "false", "False", "FALSE"]
    POSSIBLE_VALUE = TRUE_VALUES + FALSE_VALUES

    async def from_path(self, value: str) -> bool | None:
        if value in self.POSSIBLE_VALUE:
            return value in self.TRUE_VALUES

        raise NotFoundError()

    async def to_path(self, obj: bool) -> str:
        return str(obj)
