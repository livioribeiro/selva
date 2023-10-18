from decimal import Decimal
from pathlib import PurePath

from selva.di.decorator import service
from selva.web.converter.param_converter import ParamConverter
from selva.web.exception import HTTPBadRequestException


@service(provides=ParamConverter[str])
class StrParamConverter:
    @staticmethod
    def from_param(value: str) -> str:
        return value

    @staticmethod
    def into_str(data: str) -> str:
        return data


@service(provides=ParamConverter[int])
class IntParamConverter:
    @staticmethod
    def from_param(value: str) -> int:
        try:
            return int(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@service(provides=ParamConverter[float])
class FloatParamConverter:
    @staticmethod
    def from_param(value: str) -> float:
        try:
            return float(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@service(provides=ParamConverter[Decimal])
class DecimalParamConverter:
    @staticmethod
    def from_param(value: str) -> Decimal:
        try:
            return Decimal(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@service(provides=ParamConverter[bool])
class BoolParamConverter:
    TRUE_VALUES = ["1", "true"]
    FALSE_VALUES = ["0", "false"]

    @staticmethod
    def from_param(value: str) -> bool:
        if value.lower() in BoolParamConverter.TRUE_VALUES:
            return True
        if value.lower() in BoolParamConverter.FALSE_VALUES:
            return False

        raise HTTPBadRequestException()

    @staticmethod
    def into_str(data: bool) -> str:
        return "true" if data else "false"


@service(provides=ParamConverter[PurePath])
class PurePathParamConverter:
    @staticmethod
    def from_param(value: str) -> PurePath:
        return PurePath(value)

    @staticmethod
    def into_str(data: PurePath) -> str:
        return "/".join(data.parts)
