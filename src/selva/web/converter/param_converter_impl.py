import decimal
from decimal import Decimal
from pathlib import PurePath

from selva.web.converter.decorator import register_converter
from selva.web.exception import HTTPBadRequestException


@register_converter(str, str)
class StrParamConverter:
    @staticmethod
    def convert(value: str, _original_type: type[str]) -> str:
        return value


@register_converter(str, int)
class IntParamConverter:
    @staticmethod
    def convert(value: str, _original_type: type[int]) -> int:
        try:
            return int(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@register_converter(str, float)
class FloatParamConverter:
    @staticmethod
    def convert(value: str, _original_type: type[float]) -> float:
        try:
            return float(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err


@register_converter(str, Decimal)
class DecimalParamConverter:
    @staticmethod
    def convert(value: str, _original_type: type[Decimal]) -> Decimal:
        try:
            return Decimal(value)
        except decimal.InvalidOperation as err:
            raise HTTPBadRequestException() from err


@register_converter(str, bool)
class BoolParamConverter:
    TRUE_VALUES = ["1", "true"]
    FALSE_VALUES = ["0", "false"]

    @staticmethod
    def convert(value: str, _original_type: type[bool]) -> bool:
        if value.lower() in BoolParamConverter.TRUE_VALUES:
            return True
        if value.lower() in BoolParamConverter.FALSE_VALUES:
            return False

        raise HTTPBadRequestException()


@register_converter(str, PurePath)
class PurePathParamConverter:
    @staticmethod
    def convert(value: str, _original_type: type[PurePath]) -> PurePath:
        return PurePath(value)
