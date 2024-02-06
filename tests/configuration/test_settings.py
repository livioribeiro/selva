import logging
import os
from pathlib import Path

import pytest

from selva.configuration.defaults import default_settings
from selva.configuration.settings import (
    Settings,
    SettingsError,
    _get_settings_nocache,
    get_settings_for_profile,
    merge_recursive,
)


def test_get_settings(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "base")

    result = _get_settings_nocache()
    assert result == default_settings | {
        "prop": "value",
        "list": ["1", "2", "3"],
        "dict": Settings(
            {
                "a": "1",
                "b": "2",
                "c": "3",
            }
        ),
    }


@pytest.mark.parametrize(
    "profile",
    ["dev", "stg", "prd"],
)
def test_get_settings_with_profile(monkeypatch, profile):
    monkeypatch.chdir(Path(__file__).parent / "profiles")
    monkeypatch.setenv("SELVA_PROFILE", profile)

    result = _get_settings_nocache()
    assert result == default_settings | {
        "name": "application",
        "environment": profile,
    }


@pytest.mark.parametrize(
    "profile,expected",
    [
        (None, {"name": "application"}),
        ("dev", {"environment": "dev"}),
        ("stg", {"environment": "stg"}),
        ("prd", {"environment": "prd"}),
    ],
    ids=["None", "dev", "stg", "prd"],
)
def test_get_settings_for_profile(monkeypatch, profile, expected):
    monkeypatch.chdir(Path(__file__).parent / "profiles")

    result = get_settings_for_profile(profile)
    assert result == expected


def test_empty_settings_file(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "empty")

    result = get_settings_for_profile()
    assert result == {}


def test_configure_settings_dir(monkeypatch):
    monkeypatch.setenv(
        "SELVA_SETTINGS_DIR",
        str(Path(__file__).parent / "base" / "configuration"),
    )

    result = _get_settings_nocache()
    assert result == default_settings | {
        "prop": "value",
        "list": ["1", "2", "3"],
        "dict": Settings(
            {
                "a": "1",
                "b": "2",
                "c": "3",
            }
        ),
    }


def test_configure_settings_file(monkeypatch):
    monkeypatch.chdir(str(Path(__file__).parent / "alternate"))
    monkeypatch.setenv(
        "SELVA_SETTINGS_FILE",
        "application.yaml",
    )

    result = _get_settings_nocache()
    assert result == default_settings | {
        "prop": "value",
        "list": ["1", "2", "3"],
        "dict": Settings(
            {
                "a": "1",
                "b": "2",
                "c": "3",
            }
        ),
    }


def test_configure_settings_dir_and_file(monkeypatch):
    monkeypatch.setenv(
        "SELVA_SETTINGS_DIR",
        str(Path(__file__).parent / "alternate" / "configuration"),
    )
    monkeypatch.setenv(
        "SELVA_SETTINGS_FILE",
        "application.yaml",
    )

    result = _get_settings_nocache()
    assert result == default_settings | {
        "prop": "value",
        "list": ["1", "2", "3"],
        "dict": Settings(
            {
                "a": "1",
                "b": "2",
                "c": "3",
            }
        ),
    }


def test_configure_settings_file_with_profile(monkeypatch):
    monkeypatch.chdir(str(Path(__file__).parent / "alternate"))
    monkeypatch.setenv(
        "SELVA_SETTINGS_FILE",
        "application.yaml",
    )

    monkeypatch.setenv("SELVA_PROFILE", "prd")

    result = _get_settings_nocache()
    assert result == default_settings | {
        "environment": "prd",
        "prop": "value",
        "list": ["1", "2", "3"],
        "dict": {
            "a": "1",
            "b": "2",
            "c": "3",
        },
    }


@pytest.mark.parametrize(
    "env",
    ["dev", "stg", "prd"],
)
def test_configure_env_setttings(monkeypatch, env):
    monkeypatch.setenv(
        "SELVA_SETTINGS_DIR",
        str(Path(__file__).parent / "profiles/configuration"),
    )
    monkeypatch.setenv("SELVA_PROFILE", env)

    result = _get_settings_nocache()
    assert result == default_settings | {
        "name": "application",
        "environment": env,
    }


@pytest.mark.parametrize(
    "env",
    ["dev", "stg", "prd"],
)
def test_override_settings(monkeypatch, env):
    monkeypatch.chdir(Path(__file__).parent / "override")

    result = _get_settings_nocache()
    assert result == default_settings | {"value": "base"}

    monkeypatch.setenv("SELVA_PROFILE", env)

    result = _get_settings_nocache()
    assert result == default_settings | {"value": env}


def test_settings_class(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "base")

    settings = _get_settings_nocache()
    assert settings["prop"] == "value"
    assert settings["list"] == ["1", "2", "3"]
    assert settings["dict"] == {
        "a": "1",
        "b": "2",
        "c": "3",
    }


@pytest.mark.parametrize(
    "env",
    ["dev", "stg", "prd"],
)
def test_setttings_class_env(monkeypatch, env):
    monkeypatch.chdir(Path(__file__).parent / "profiles")
    monkeypatch.setenv("SELVA_PROFILE", env)

    settings = _get_settings_nocache()
    assert settings["name"] == "application"
    assert settings["environment"] == env


def test_no_profile_settings_file_should_log_warning(monkeypatch, caplog):
    monkeypatch.chdir(Path(__file__).parent / "profiles")

    profile = "does_not_exist"
    monkeypatch.setenv("SELVA_PROFILE", profile)

    settings_path = Path.cwd() / "configuration" / f"settings_{profile}.yaml"

    with caplog.at_level(logging.WARNING, logger="selva"):
        _get_settings_nocache()

    assert (
        f"no settings file found for profile '{profile}' at {settings_path}"
        in caplog.text
    )


def test_override_settings_with_env_var(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "base")
    monkeypatch.setenv("SELVA__PROP", "override")

    settings = _get_settings_nocache()

    assert settings.prop == "override"


def test_override_nested_settings_with_env_var(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "base")
    monkeypatch.setenv("SELVA__DICT__A", "override")

    settings = _get_settings_nocache()

    assert settings.dict.a == "override"


def test_non_existent_env_var_should_fail(monkeypatch):
    monkeypatch.chdir(
        Path(__file__).parent / "invalid_configuration" / "non_existent_env_var"
    )

    with pytest.raises(
        ValueError,
        match=f"DOES_NOT_EXIST environment variable is not defined and does not contain a default value",
    ):
        _get_settings_nocache()


def test_invalid_yaml_should_fail(monkeypatch):
    settings_path = Path(__file__).parent / "invalid_configuration" / "invalid_yaml"
    monkeypatch.chdir(Path(__file__).parent / "invalid_configuration" / "invalid_yaml")

    with pytest.raises(
        SettingsError, match=f"cannot load settings from {settings_path}"
    ):
        get_settings_for_profile()


@pytest.mark.parametrize(
    "settings,extra,expected",
    [
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        ({"a": 1}, {"a": 2}, {"a": 2}),
        ({"a": {"a": 1}}, {"a": {"b": 2}}, {"a": {"a": 1, "b": 2}}),
        ({"a": {"a": 1}}, {"a": {"a": 2}}, {"a": {"a": 2}}),
        ({"a": {"a": 1}}, {"a": 1}, {"a": 1}),
        ({"a": 1}, {"a": {"a": 1}}, {"a": {"a": 1}}),
    ],
    ids=[
        "add value",
        "replace value",
        "add nested value",
        "replace nested value",
        "replace dict with value",
        "replace value with dict",
    ],
)
def test_merge_recursive(settings, extra, expected):
    merge_recursive(settings, extra)

    assert settings == expected


def test_settings_item_access():
    settings = Settings({"a": 1})

    assert settings["a"] == 1


def test_settings_nested_item_access():
    settings = Settings({"a": {"b": 1}})

    assert settings["a"]["b"] == 1


def test_settings_attribute_access():
    settings = Settings({"a": 1})

    assert settings.a == 1


def test_settings_nested_attribute_access():
    settings = Settings({"a": {"b": 1}})

    assert settings.a.b == 1


def test_settings_non_existent_attribute_should_fail():
    settings = Settings({})

    with pytest.raises(AttributeError, match="a"):
        settings.a


def test_settings_mixed_item_attribute_access():
    settings = Settings({"a": {"b": 1}})

    assert settings["a"].b == 1
    assert settings.a["b"] == 1


def test_settings_method_access():
    settings = Settings({"a": 1})

    assert settings.get("a") == 1


def test_settings_method_access_default_value():
    settings = Settings({})

    assert settings.get("a") is None
    assert settings.get("a", "b") == "b"


def test_settings_get_nonexistent_item_should_fail():
    settings = Settings({})
    with pytest.raises(KeyError, match="a"):
        settings["a"]


def test_settings_with_env_var(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "env_var")
    monkeypatch.setenv("VAR_NAME", "test")

    settings = _get_settings_nocache()
    assert settings.name == "test"


def test_settings_with_env_var_replaced_in_profile(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "env_var")
    monkeypatch.setenv("SELVA_PROFILE", "profile")

    settings = _get_settings_nocache()
    assert settings.name == "profile"
