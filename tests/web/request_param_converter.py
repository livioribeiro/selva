from pathlib import PurePath

import pytest

from selva.web.converter.param_converter_impl import (
    StrRequestParamConverter,
    IntRequestParamConverter,
    FloatRequestParamConverter,
    BoolRequestParamConverter,
    PurePathRequestParamConverter,
)

from selva.web.error import HTTPNotFoundError


async def test_str_param_converter():
    converter = StrRequestParamConverter()
    original = "A"
    converted = "A"

    result = converter.convert(original)
    assert result == converted

    result_reverse = converter.convert_back(result)
    assert result_reverse == original


async def test_int_param_converter():
    converter = IntRequestParamConverter()
    original = "1"
    converted = 1

    result = converter.convert(original)
    assert result == converted

    result_reverse = converter.convert_back(result)
    assert result_reverse == original


async def test_float_param_converter():
    converter = FloatRequestParamConverter()
    original = "1.1"
    converted = 1.1

    result = converter.convert(original)
    assert result == converted

    result_reverse = converter.convert_back(result)
    assert result_reverse == original


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
    ]
)
async def test_bool_param_converter(value: str, expected: bool):
    converter = BoolRequestParamConverter()

    result = converter.convert(value)
    assert result == expected

    result_reverse = converter.convert_back(result)
    assert result_reverse == str(expected).lower()


async def test_bool_param_invalid_value_should_raise_error():
    converter = BoolRequestParamConverter()
    with pytest.raises(HTTPNotFoundError):
        converter.convert("invalid")


async def test_path_param_converter():
    converter = PurePathRequestParamConverter()

    original = "/path/subpath"
    converted = PurePath("/path") / "subpath"

    result = converter.convert(original)
    assert result == converted

    result_reverse = converter.convert_back(result)
    assert result_reverse == original
