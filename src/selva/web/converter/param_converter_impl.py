from pathlib import PurePath

from selva.di.decorator import service
from selva.web.converter.param_converter import RequestParamConverter
from selva.web.error import HTTPNotFoundError


@service(provides=RequestParamConverter[str])
class StrRequestParamConverter:
    def convert(self, value: str) -> str:
        return value

    def convert_back(self, obj: str) -> str:
        return obj


@service(provides=RequestParamConverter[int])
class IntRequestParamConverter:
    def convert(self, value: str) -> int | None:
        try:
            return int(value)
        except ValueError:
            raise HTTPNotFoundError()

    def convert_back(self, obj: int) -> str:
        return str(obj)


@service(provides=RequestParamConverter[float])
class FloatRequestParamConverter:
    def convert(self, value: str) -> float | None:
        try:
            return float(value)
        except ValueError:
            raise HTTPNotFoundError()

    def convert_back(self, obj: float) -> str:
        return str(obj)


@service(provides=RequestParamConverter[bool])
class BoolRequestParamConverter:
    TRUE_VALUES = ["1", "true"]
    FALSE_VALUES = ["0", "false"]

    def convert(self, value: str) -> bool | None:
        if value.lower() in BoolRequestParamConverter.TRUE_VALUES:
            return True
        if value.lower() in BoolRequestParamConverter.FALSE_VALUES:
            return False

        raise HTTPNotFoundError()

    def convert_back(self, obj: bool) -> str:
        return str(obj).lower()


@service(provides=RequestParamConverter[PurePath])
class PurePathRequestParamConverter:
    def convert(self, value: str) -> PurePath:
        return PurePath(value)

    def convert_back(self, obj: PurePath) -> str:
        return obj.as_posix()
