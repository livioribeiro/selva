import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from selva.configuration.settings import (
    Settings,
    SettingsModuleError,
    extract_valid_keys,
    get_default_settings,
    get_settings,
    get_settings_for_env,
    is_valid_conf,
)


@pytest.mark.parametrize(
    "name",
    [
        "ALL_UPPERCASE",
        "WITH_NUMBER_1",
        "MULTI__UNDERSCORE",
        "END_WITH_UNDERLINE_",
    ],
)
def test_valid_config_names(name: str):
    result = is_valid_conf(name)
    assert result


@pytest.mark.parametrize(
    "name",
    [
        "all_undercase",
        "ONE_UNDERCASe",
        "_STARTS_WITH_UNDERSCORE",
    ],
)
def test_invalid_config_names(name: str):
    result = is_valid_conf(name)
    assert not result


def test_extract_valid_settings():
    module = SimpleNamespace()
    module.ALL_UPPERCASE = ""
    module.WITH_NUMBER_1 = ""
    module.MULTI__UNDERSCORE = ""
    module.END_WITH_UNDERLINE_ = ""
    module.all_undercase = ""
    module.ONE_UNDERCASe = ""
    module._STARTS_WITH_UNDERSCORE = ""

    result = extract_valid_keys(module)
    assert result == {
        "ALL_UPPERCASE": "",
        "WITH_NUMBER_1": "",
        "MULTI__UNDERSCORE": "",
        "END_WITH_UNDERLINE_": "",
    }


@pytest.mark.parametrize(
    "env,expected",
    [
        (None, {"NAME": "application"}),
        ("dev", {"ENVIRONMENT": "dev"}),
        ("hlg", {"ENVIRONMENT": "hlg"}),
        ("prd", {"ENVIRONMENT": "prd"}),
    ],
    ids=["None", "dev", "hlg", "prd"],
)
def test_get_settings_for_env(monkeypatch, env, expected):
    monkeypatch.chdir(Path(__file__).parent / "envs")

    result = get_settings_for_env(env)
    assert result == expected


def test_get_settings(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "base")

    result = get_settings()
    assert result.__dict__ == get_default_settings() | {
        "CONF_STR": "str",
        "CONF_INT": 1,
        "CONF_LIST": [1, 2, 3],
        "CONF_DICT": {
            "a": 1,
            "b": 2,
            "c": 3,
        },
    }


def test_configure_settings_module(monkeypatch):
    monkeypatch.setenv(
        "SELVA_SETTINGS_MODULE",
        str(Path(__file__).parent / "base/configuration/settings"),
    )

    result = get_settings()
    assert result.__dict__ == get_default_settings() | {
        "CONF_STR": "str",
        "CONF_INT": 1,
        "CONF_LIST": [1, 2, 3],
        "CONF_DICT": {
            "a": 1,
            "b": 2,
            "c": 3,
        },
    }


@pytest.mark.parametrize(
    "env",
    ["dev", "hlg", "prd"],
)
def test_get_env_setttings(monkeypatch, env):
    monkeypatch.chdir(Path(__file__).parent / "envs")
    monkeypatch.setenv("SELVA_ENV", env)

    result = get_settings()
    assert result.__dict__ == get_default_settings() | {
        "NAME": "application",
        "ENVIRONMENT": env,
    }


@pytest.mark.parametrize(
    "env",
    ["dev", "hlg", "prd"],
)
def test_configure_env_setttings_module(monkeypatch, env):
    monkeypatch.setenv(
        "SELVA_SETTINGS_MODULE",
        str(Path(__file__).parent / "envs/configuration/settings"),
    )
    monkeypatch.setenv("SELVA_ENV", env)

    result = get_settings()
    assert result.__dict__ == get_default_settings() | {
        "NAME": "application",
        "ENVIRONMENT": env,
    }


@pytest.mark.parametrize(
    "env",
    ["dev", "hlg", "prd"],
)
def test_override_settings(monkeypatch, env):
    default_settings = get_default_settings()
    monkeypatch.chdir(Path(__file__).parent / "override")

    result = get_settings()
    assert result.__dict__ == default_settings | {"VALUE": "base"}

    monkeypatch.setenv("SELVA_ENV", env)

    result = get_settings()
    assert result.__dict__ == default_settings | {"VALUE": env}


def test_settings_class(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "base")

    settings = get_settings()
    assert settings.CONF_STR == "str"
    assert settings.CONF_INT == 1
    assert settings.CONF_LIST == [1, 2, 3]
    assert settings.CONF_DICT == {
        "a": 1,
        "b": 2,
        "c": 3,
    }


@pytest.mark.parametrize(
    "env",
    ["dev", "hlg", "prd"],
)
def test_setttings_class_env(monkeypatch, env):
    monkeypatch.chdir(Path(__file__).parent / "envs")
    monkeypatch.setenv("SELVA_ENV", env)

    settings = get_settings()
    assert settings.NAME == "application"
    assert settings.ENVIRONMENT == env


def test_no_settings_file_should_log_info(monkeypatch, caplog):
    monkeypatch.setenv("SELVA_SETTINGS_MODULE", "does_not_exist.py")

    settings_path = Path.cwd() / "does_not_exist.py"

    with caplog.at_level(logging.INFO, logger="selva"):
        get_settings()

    assert f"settings module not found: {settings_path}" in caplog.text


def test_no_env_settings_file_should_log_info(monkeypatch, caplog):
    monkeypatch.chdir(Path(__file__).parent / "envs")
    monkeypatch.setenv("SELVA_ENV", "does_not_exist")

    settings_path = Path.cwd() / "configuration" / "settings_does_not_exist.py"

    with caplog.at_level(logging.INFO, logger="selva"):
        get_settings()

    assert f"settings module not found: {settings_path}" in caplog.text


def test_invalid_settings_module_should_fail(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "invalid_settings")
    with pytest.raises(SettingsModuleError):
        get_settings()


def test_non_existent_environment_variable_should_fail(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "invalid_environment" / "non_existent")
    with pytest.raises(
        KeyError, match=f"Environment variable 'DOES_NOT_EXIST' is not defined"
    ):
        get_settings_for_env()


@pytest.mark.parametrize("value_type", ["int", "float", "bool", "dict", "json"])
def test_invalid_value_should_fail(monkeypatch, value_type):
    monkeypatch.chdir(Path(__file__).parent / "invalid_environment" / "invalid_value")
    monkeypatch.setenv("INVALID", "abc")

    message = (
        "Environment variable 'INVALID'"
        f" is not compatible with type '{value_type}': 'abc'"
    )

    with pytest.raises(ValueError, match=message):
        get_settings_for_env(value_type)


def test_settings_attribute_access():
    settings = Settings({"A": 1})

    assert settings.A == 1


def test_settings_method_access():
    settings = Settings({"A": 1})

    assert settings.get("A") == 1


def test_settings_method_access_default_value():
    settings = Settings({})

    assert settings.get("A") is None
    assert settings.get("A", "B") == "B"


def test_settings_item_access():
    settings = Settings({"A": 1})

    assert settings["A"] == 1


def test_settings_set_attribute_should_fail():
    settings = Settings({})
    with pytest.raises(AttributeError, match="can't set attribute"):
        settings.A = 1


def test_settings_setattr_should_fail():
    settings = Settings({})
    with pytest.raises(AttributeError, match="can't set attribute"):
        setattr(settings, "A", 1)


def test_settings_del_attribute_should_fail():
    settings = Settings({"A": 1})
    with pytest.raises(AttributeError, match="can't del attribute"):
        del settings.A


def test_settings_delattr_should_fail():
    settings = Settings({"A": 1})
    with pytest.raises(AttributeError, match="can't del attribute"):
        delattr(settings, "A")


def test_settings_get_nonexistent_item_should_fail():
    settings = Settings({})
    with pytest.raises(KeyError, match="A"):
        settings["A"]
