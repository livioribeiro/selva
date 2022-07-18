from selva.web.errors import NotFoundError

from .path_converter import PathConverter


class StrPathConverter(PathConverter[str]):
    def from_path(self, value: str) -> str:
        return value

    def into_path(self, obj: str) -> str:
        return obj


class IntPathConverter(PathConverter[int]):
    def from_path(self, value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            raise NotFoundError()

    def into_path(self, obj: int) -> str:
        return str(obj)


class FloatPathConverter(PathConverter[float]):
    def from_path(self, value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            raise NotFoundError()

    def into_path(self, obj: float) -> str:
        return str(obj)


class BoolPathConverter(PathConverter[bool]):
    TRUE_VALUES = ["1", "true", "True", "TRUE"]
    FALSE_VALUES = ["0", "false", "False", "FALSE"]
    POSSIBLE_VALUE = TRUE_VALUES + FALSE_VALUES

    def from_path(self, value: str) -> bool | None:
        if value in self.POSSIBLE_VALUE:
            return value in self.TRUE_VALUES

        raise NotFoundError()

    def into_path(self, obj: bool) -> str:
        return str(obj)
