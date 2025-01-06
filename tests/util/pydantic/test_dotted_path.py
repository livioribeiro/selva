import pytest
from pydantic import BaseModel

from selva._util.pydantic.dotted_path import DottedPath


class Item:
    pass


class MyModel(BaseModel):
    item: DottedPath


def test_dotted_path():
    result = MyModel.model_validate({"item": f"{Item.__module__}:{Item.__qualname__}"})
    assert result.item is Item


def test_invalid_dotted_path():
    with pytest.raises(ValueError):
        MyModel.model_validate({"item": "invalid.dotted:path"})
