from pathlib import PurePath

from selva.di.decorator import service
from selva.web.converter.path_converter import PathParamConverter
from selva.web.error import HTTPNotFoundError


class StrPathParamConverter(PathParamConverter[str]):
    def from_path(self, value: str) -> str:
        return value

    def into_path(self, obj: str) -> str:
        return obj


class IntPathParamConverter(PathParamConverter[int]):
    def from_path(self, value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            raise HTTPNotFoundError()

    def into_path(self, obj: int) -> str:
        return str(obj)


class FloatPathParamConverter(PathParamConverter[float]):
    def from_path(self, value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            raise HTTPNotFoundError()

    def into_path(self, obj: float) -> str:
        return str(obj)


class BoolPathParamConverter(PathParamConverter[bool]):
    TRUE_VALUES = ["1", "true", "True", "TRUE"]
    FALSE_VALUES = ["0", "false", "False", "FALSE"]
    POSSIBLE_VALUE = TRUE_VALUES + FALSE_VALUES

    def from_path(self, value: str) -> bool | None:
        if value in self.POSSIBLE_VALUE:
            return value in self.TRUE_VALUES

        raise HTTPNotFoundError()

    def into_path(self, obj: bool) -> str:
        return str(obj)


class PurePathPathParamConverter(PathParamConverter[PurePath]):
    def from_path(self, value: str) -> PurePath:
        return PurePath(value)

    def into_path(self, obj: PurePath) -> str:
        return obj.as_posix()
