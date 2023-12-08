from typing import Annotated

import pytest
from pydantic import BaseModel

from selva._util.pydantic.dotted_path import DottedPath


class Item:
    pass


class TestModel(BaseModel):
    item: Annotated[type, DottedPath]


def test_dotted_path():
    result = TestModel(item=f"{Item.__module__}.{Item.__qualname__}")
    assert result.item is Item


def test_invalid_dotted_path():
    with pytest.raises(ValueError):
        TestModel(item="invalid.dotted.path")
