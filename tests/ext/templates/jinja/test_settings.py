import jinja2
import pytest
from pydantic import ValidationError

from selva.ext.templates.jinja.settings import JinjaTemplateSettings


class MyUndefined(jinja2.Undefined):
    pass


def finalize():
    pass


def autoescape():
    pass


class MyBytecodeCache(jinja2.BytecodeCache):
    pass


my_bytecode_cache = MyBytecodeCache()


def test_jinja_settings():
    settings = JinjaTemplateSettings.model_validate(
        {
            "undefined": f"{MyUndefined.__module__}:{MyUndefined.__qualname__}",
            "finalize": f"{finalize.__module__}:{finalize.__qualname__}",
            "autoescape": f"{autoescape.__module__}:{autoescape.__qualname__}",
            "bytecode_cache": f"{my_bytecode_cache.__module__}:my_bytecode_cache",
        },
    )

    assert settings.undefined is MyUndefined
    assert settings.finalize is finalize
    assert settings.autoescape is autoescape
    assert settings.bytecode_cache is my_bytecode_cache


@pytest.mark.parametrize(
    "value,expected",
    [
        (True, True),
        ("true", True),
        ("True", True),
        (False, False),
        ("false", False),
        ("False", False),
    ],
)
def test_autoescape_bool(value, expected):
    settings = JinjaTemplateSettings.model_validate({"autoescape": value})
    assert settings.autoescape is expected


def test_invalid_undefined_should_fail():
    with pytest.raises(ValidationError):
        JinjaTemplateSettings.model_validate({"undefined": 1})


def test_invalid_import_undefined_should_fail():
    with pytest.raises(ValidationError):
        JinjaTemplateSettings.model_validate({"undefined": "does.not.exist"})


def test_invalid_finalize_should_fail():
    with pytest.raises(ValidationError):
        JinjaTemplateSettings.model_validate({"finalize": 1})


def test_invalid_import_finalize_should_fail():
    with pytest.raises(ValidationError):
        JinjaTemplateSettings.model_validate({"finalize": "does.not.exist"})


def test_invalid_autoescape_should_fail():
    with pytest.raises(ValidationError):
        model = JinjaTemplateSettings.model_validate({"autoescape": "invalid"})
        repr(model)


def test_invalid_import_autoescape_should_fail():
    with pytest.raises(ValidationError):
        JinjaTemplateSettings.model_validate({"autoescape": "does.not.exist"})
