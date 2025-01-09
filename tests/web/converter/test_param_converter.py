from decimal import Decimal
from pathlib import PurePath

import pytest

from selva.web.converter.param_converter_impl import (
    BoolParamConverter,
    DecimalParamConverter,
    FloatParamConverter,
    IntParamConverter,
    PurePathParamConverter,
    StrParamConverter,
)
from selva.web.exception import HTTPBadRequestException


async def test_str_request_param():
    converter = StrParamConverter()
    value = "A"
    expected = "A"

    result = converter.convert(value, str)
    assert result == expected


async def test_int_request_param():
    converter = IntParamConverter()
    value = "1"
    expected = 1

    result = converter.convert(value, int)
    assert result == expected


def test_int_request_param_with_invalid_value_should_fail():
    converter = IntParamConverter()
    with pytest.raises(HTTPBadRequestException):
        converter.convert("A", int)


async def test_float_request_param():
    converter = FloatParamConverter()
    value = "1.1"
    expected = 1.1

    result = converter.convert(value, float)
    assert result == expected


def test_float_request_param_with_invalid_value_should_fail():
    converter = FloatParamConverter()
    with pytest.raises(HTTPBadRequestException):
        converter.convert("A", float)


async def test_decimal_request_param():
    converter = DecimalParamConverter()
    value = "1.1"
    expected = Decimal("1.1")

    result = converter.convert(value, Decimal)
    assert result == expected


def test_decimal_request_param_with_invalid_value_should_fail():
    converter = DecimalParamConverter()
    with pytest.raises(HTTPBadRequestException):
        converter.convert("A", Decimal)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1", True),
        ("True", True),
        ("true", True),
        ("tRuE", True),
        ("0", False),
        ("False", False),
        ("false", False),
        ("fAlSe", False),
    ],
    ids=["1", "True", "true", "tRuE", "0", "False", "false", "fAlSe"],
)
async def test_bool_request_param(value: str, expected: bool):
    converter = BoolParamConverter()

    result = converter.convert(value, bool)
    assert result == expected


async def test_bool_request_param_with_invalid_value_should_fail():
    converter = BoolParamConverter()
    with pytest.raises(HTTPBadRequestException):
        converter.convert("invalid", bool)


async def test_path_request_param():
    converter = PurePathParamConverter()

    value = "/path/subpath"
    expected = PurePath("/path", "subpath")

    result = converter.convert(value, PurePath)
    assert result == expected
