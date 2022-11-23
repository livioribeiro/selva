from pathlib import PurePath

from selva.di.decorators import service
from selva.web.converter.path_converter import PathConverter
from selva.web.errors import HTTPNotFoundError


@service(provides=PathConverter[str])
class StrPathConverter:
    def from_path(self, value: str) -> str:
        return value

    def into_path(self, obj: str) -> str:
        return obj


@service(provides=PathConverter[int])
class IntPathConverter:
    def from_path(self, value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            raise HTTPNotFoundError()

    def into_path(self, obj: int) -> str:
        return str(obj)


@service(provides=PathConverter[float])
class FloatPathConverter:
    def from_path(self, value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            raise HTTPNotFoundError()

    def into_path(self, obj: float) -> str:
        return str(obj)


@service(provides=PathConverter[bool])
class BoolPathConverter:
    TRUE_VALUES = ["1", "true", "True", "TRUE"]
    FALSE_VALUES = ["0", "false", "False", "FALSE"]
    POSSIBLE_VALUE = TRUE_VALUES + FALSE_VALUES

    def from_path(self, value: str) -> bool | None:
        if value in self.POSSIBLE_VALUE:
            return value in self.TRUE_VALUES

        raise HTTPNotFoundError()

    def into_path(self, obj: bool) -> str:
        return str(obj)


@service(provides=PathConverter[PurePath])
class PurePathPathConverter:
    def from_path(self, value: str) -> PurePath:
        return PurePath(value)

    def into_path(self, obj: PurePath) -> str:
        return obj.as_posix()
