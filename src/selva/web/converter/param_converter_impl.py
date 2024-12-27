from decimal import Decimal
from pathlib import PurePath

from selva.di.decorator import service
from selva.web.converter.param_converter import ParamConverter
from selva.web.exception import HTTPBadRequestException


@service
async def str_param_converter(_) -> ParamConverter[str]:
    return StrParamConverter()


@service
async def int_param_converter(_) -> ParamConverter[int]:
    return IntParamConverter()


@service
async def float_param_converter(_) -> ParamConverter[float]:
    return FloatParamConverter()


@service
async def decimal_param_converter(_) -> ParamConverter[Decimal]:
    return DecimalParamConverter()


@service
async def bool_param_converter(_) -> ParamConverter[bool]:
    return BoolParamConverter()


@service
async def path_param_converter(_) -> ParamConverter[PurePath]:
    return PurePathParamConverter()


class StrParamConverter:
    @staticmethod
    def from_str(value: str) -> str:
        return value

    @staticmethod
    def into_str(data: str) -> str:
        return data


class IntParamConverter:
    @staticmethod
    def from_str(value: str) -> int:
        try:
            return int(value)
        except ValueError as err:
            raise HTTPBadRequestException()

    @staticmethod
    def into_str(data: int) -> str:
        return str(data)


class FloatParamConverter:
    @staticmethod
    def from_str(value: str) -> float:
        try:
            return float(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err

    @staticmethod
    def into_str(data: float) -> str:
        return str(data)


class DecimalParamConverter:
    @staticmethod
    def from_str(value: str) -> Decimal:
        try:
            return Decimal(value)
        except ValueError as err:
            raise HTTPBadRequestException() from err

    @staticmethod
    def into_str(data: Decimal) -> str:
        return str(data)


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


class PurePathParamConverter:
    @staticmethod
    def from_str(value: str) -> PurePath:
        return PurePath(value)

    @staticmethod
    def into_str(data: PurePath) -> str:
        return "/".join(data.parts)
