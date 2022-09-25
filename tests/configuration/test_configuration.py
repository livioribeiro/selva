from pathlib import Path
from types import SimpleNamespace

import pytest

from selva.configuration import (
    is_valid_conf,
    extract_valid_keys,
    get_settings,
    Settings,
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
    ]
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


def test_get_settings(monkeypatch):
    monkeypatch.syspath_prepend(Path(__file__).parent / "base")

    result = get_settings()
    assert result == {
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
    monkeypatch.setenv("SELVA_SETTINGS_MODULE", "tests.configuration.base.configuration.settings")

    result = get_settings()
    assert result == {
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
def test_get_setttings_env(monkeypatch, env):
    monkeypatch.syspath_prepend(Path(__file__).parent / "envs")
    monkeypatch.setenv("SELVA_ENV", env)

    result = get_settings()
    assert result == {
        "NAME": "application",
        "ENVIRONMENT": env,
    }


@pytest.mark.parametrize(
    "env",
    ["dev", "hlg", "prd"],
)
def test_configure_setttings_module_env(monkeypatch, env):
    monkeypatch.setenv("SELVA_SETTINGS_MODULE", "tests.configuration.envs.configuration.settings")
    monkeypatch.setenv("SELVA_ENV", env)

    result = get_settings()
    assert result == {
        "NAME": "application",
        "ENVIRONMENT": env,
    }


def test_settings_class(monkeypatch):
    monkeypatch.syspath_prepend(Path(__file__).parent / "base")

    settings = Settings()
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
    monkeypatch.syspath_prepend(Path(__file__).parent / "envs")
    monkeypatch.setenv("SELVA_ENV", env)

    settings = Settings()
    assert settings.NAME == "application"
    assert settings.ENVIRONMENT == env
