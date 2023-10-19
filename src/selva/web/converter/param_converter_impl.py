from decimal import Decimal
from pathlib import PurePath

from selva.web.converter.decorator import register_param_converter
from selva.web.exception import HTTPBadRequestException


@register_param_converter(str)
class StrParamConverter:
    @staticmethod
    def from_str(value: str) -> str:
        return value

    @staticmethod
    def into_str(data: str) -> str:
        return data


@register_param_converter(int)
class IntParamConverter:
    @staticmethod
    def from_str(value: str) -> int:
        try:
            return int(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@register_param_converter(float)
class FloatParamConverter:
    @staticmethod
    def from_str(value: str) -> float:
        try:
            return float(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@register_param_converter(Decimal)
class DecimalParamConverter:
    @staticmethod
    def from_str(value: str) -> Decimal:
        try:
            return Decimal(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@register_param_converter(bool)
class BoolParamConverter:
    TRUE_VALUES = ["1", "true"]
    FALSE_VALUES = ["0", "false"]

    @staticmethod
    def from_str(value: str) -> bool:
        if value.lower() in BoolParamConverter.TRUE_VALUES:
            return True
        if value.lower() in BoolParamConverter.FALSE_VALUES:
            return False

        raise HTTPBadRequestException()

    @staticmethod
    def into_str(data: bool) -> str:
        return "true" if data else "false"


@register_param_converter(PurePath)
class PurePathParamConverter:
    @staticmethod
    def from_str(value: str) -> PurePath:
        return PurePath(value)

    @staticmethod
    def into_str(data: PurePath) -> str:
        return "/".join(data.parts)
