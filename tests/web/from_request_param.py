from pathlib import PurePath

import pytest

from selva.web.converter.from_request_param_impl import (
    StrFromRequestParam,
    IntFromRequestParam,
    FloatFromRequestParam,
    BoolFromRequestParam,
    PurePathFromRequestParam,
)

from selva.web.error import HTTPBadRequestError


async def test_str_request_param():
    converter = StrFromRequestParam()
    value = "A"
    expected = "A"

    result = converter.from_request_param(value)
    assert result == expected


async def test_int_request_param():
    converter = IntFromRequestParam()
    value = "1"
    expected = 1

    result = converter.from_request_param(value)
    assert result == expected


async def test_float_request_param():
    converter = FloatFromRequestParam()
    value = "1.1"
    expected = 1.1

    result = converter.from_request_param(value)
    assert result == expected


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
    converter = BoolFromRequestParam()

    result = converter.from_request_param(value)
    assert result == expected


async def test_bool_request_param_with_invalid_value_should_raise_error():
    converter = BoolFromRequestParam()
    with pytest.raises(HTTPBadRequestError):
        converter.from_request_param("invalid")


async def test_path_request_param():
    converter = PurePathFromRequestParam()

    value = "/path/subpath"
    expected = PurePath("/path") / "subpath"

    result = converter.from_request_param(value)
    assert result == expected
