from decimal import Decimal
from pathlib import PurePath

from selva.web.converter.decorator import register_converter
from selva.web.exception import HTTPBadRequestException


@register_converter(str, str)
class StrParamConverter:
    @staticmethod
    def convert(value: str, original_type: type[str]) -> str:
        return value

    @staticmethod
    def convert_back(data: str) -> str:
        return data


@register_converter(str, int)
class IntParamConverter:
    @staticmethod
    def convert(value: str, original_type: type[int]) -> int:
        try:
            return int(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err

    @staticmethod
    def convert_back(data: int) -> str:
        return str(data)


@register_converter(str, float)
class FloatParamConverter:
    @staticmethod
    def convert(value: str, original_type: type[float]) -> float:
        try:
            return float(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err

    @staticmethod
    def convert_back(data: float) -> str:
        return str(data)


@register_converter(str, Decimal)
class DecimalParamConverter:
    @staticmethod
    def convert(value: str, original_type: type[Decimal]) -> Decimal:
        try:
            return Decimal(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err

    @staticmethod
    def convert_back(data: Decimal) -> str:
        return str(data)


@register_converter(str, bool)
class BoolParamConverter:
    TRUE_VALUES = ["1", "true"]
    FALSE_VALUES = ["0", "false"]

    @staticmethod
    def convert(value: str, original_type: type[bool]) -> bool:
        if value.lower() in BoolParamConverter.TRUE_VALUES:
            return True
        if value.lower() in BoolParamConverter.FALSE_VALUES:
            return False

        raise HTTPBadRequestException()

    @staticmethod
    def convert_back(data: bool) -> str:
        return "true" if data else "false"


@register_converter(str, PurePath)
class PurePathParamConverter:
    @staticmethod
    def convert(value: str, original_type: type[PurePath]) -> PurePath:
        return PurePath(value)

    @staticmethod
    def convert_back(data: PurePath) -> str:
        return "/".join(data.parts)
