import os
from pathlib import Path

import pytest

from selva.configuration import (
    flatten_dict,
    get_settings,
    load_config_env,
    load_config_file,
    Settings,
)


def test_flatten_dict():
    settings = {
        "conf1": 1,
        "conf2": {
            "conf1": 1,
            "conf2": {
                "conf1": 1,
            },
        },
    }

    result = flatten_dict(settings)
    expected = {
        "conf1": 1,
        "conf2:conf1": 1,
        "conf2:conf2:conf1": 1,
    }

    assert result == expected


def test_load_config_file():
    settings_path = Path(__file__).parent / "configuration" / "test_settings.toml"
    result = load_config_file(settings_path)

    expected = {
        "conf1": 1,
        "conf2:conf1": 1,
        "conf2:conf2:conf1": 1,
    }

    assert result == expected


def test_load_config_env(monkeypatch):
    monkeypatch.setenv("SELVA_CONF1", "1")
    monkeypatch.setenv("SELVA_CONF2__CONF1", "1")
    monkeypatch.setenv("SELVA_CONF2__CONF2__CONF1", "1")

    result = load_config_env()
    expected = {
        "conf1": "1",
        "conf2:conf1": "1",
        "conf2:conf2:conf1": "1",
    }

    assert result == expected


@pytest.mark.parametrize(
    "env",
    ["dev", "hml", "prd"],
    ids=["dev", "hml", "prd"],
)
def test_get_setttings_env(monkeypatch, env):
    monkeypatch.chdir(Path(__file__).parent / "configuration" / "envs")
    monkeypatch.setenv("SELVA_ENV", env)

    result = get_settings()
    expected = {"name": "application", "env": env}

    assert result == expected


def test_get_settings_include(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "configuration" / "include")

    result = get_settings()
    expected = {"name": "application", "included": True}

    assert result == expected


def test_settings_get_str_key():
    settings = Settings({
        "conf1": 1,
        "conf2": {
            "conf1": 2,
            "conf2": {
                "conf1": 3,
            },
        },
    })

    assert settings.get("conf1") == 1
    assert settings.get("conf2:conf1") == 2
    assert settings.get("conf2:conf2:conf1") == 3


def test_settings_getitem_str_key():
    settings = Settings({
        "conf1": 1,
        "conf2": {
            "conf1": 2,
            "conf2": {
                "conf1": 3,
            },
        },
    })

    assert settings["conf1"] == 1
    assert settings["conf2:conf1"] == 2
    assert settings["conf2:conf2:conf1"] == 3


def test_settings_get_list_key():
    settings = Settings({
        "conf1": 1,
        "conf2": {
            "conf1": 2,
            "conf2": {
                "conf1": 3,
            },
        },
    })

    assert settings.get("conf1") == 1
    assert settings.get("conf2", "conf1") == 2
    assert settings.get("conf2", "conf2", "conf1") == 3


def test_settings_getitem_list_key():
    settings = Settings({
        "conf1": 1,
        "conf2": {
            "conf1": 2,
            "conf2": {
                "conf1": 3,
            },
        },
    })

    assert settings["conf1"] == 1
    assert settings["conf2", "conf1"] == 2
    assert settings["conf2", "conf2", "conf1"] == 3


def test_resources_path():
    settings = Settings()
    assert settings.resources_path == Path(os.getcwd()) / "resources"


def test_get_resource_path():
    settings = Settings()
    assert settings.get_resource_path("static") == Path(os.getcwd()) / "resources" / "static"
