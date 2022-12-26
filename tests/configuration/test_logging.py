import pytest

from selva.configuration.defaults import LOGGING as DEFAULT_CONFIG
from selva.configuration.logging import build_logging_config


def test_logging_level_config():
    loglevel_config = {
        "testloglevel": "INFO",
    }

    result = build_logging_config(DEFAULT_CONFIG, loglevel_config)
    assert result["loggers"]["testloglevel"] == {
        "level": "INFO",
        "handlers": ["console"],
    }


def test_logging_level_config_with_handler():
    loglevel_config = {
        "testloglevel": {
            "level": "INFO",
            "handlers": ["testloghandler"],
        }
    }

    result = build_logging_config(DEFAULT_CONFIG, loglevel_config)
    assert result["loggers"]["testloglevel"] == {
        "level": "INFO",
        "handlers": ["testloghandler"],
    }


def test_change_existing_logging_level():
    assert DEFAULT_CONFIG["loggers"]["selva"]["level"] == "WARNING"

    loglevel_config = {
        "selva": "INFO",
    }

    result = build_logging_config(DEFAULT_CONFIG, loglevel_config)
    assert result["loggers"]["selva"] == {"level": "INFO", "handlers": ["console"]}


def test_wrong_type_for_logging_level_should_raise_error():
    loglevel_config = {
        "testloglevel": [],
    }

    with pytest.raises(
        ValueError,
        match=f"logging level config must be str or dict, '{repr(list)}' given",
    ):
        build_logging_config(DEFAULT_CONFIG, loglevel_config)


def test_default_handler_is_first_handler():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(asctime)s %(message)s"},
        },
        "handlers": {
            "first": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "second": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "loggers": {},
    }

    loglevel_config = {"selva": "INFO"}

    result = build_logging_config(config, loglevel_config)
    assert result["loggers"]["selva"]["handlers"] == ["first"]


def test_loggers_key_should_be_created_if_not_exist():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(asctime)s %(message)s"},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
    }

    loglevel_config = {"selva": "INFO"}

    result = build_logging_config(config, loglevel_config)
    assert result["loggers"]["selva"] == {"level": "INFO", "handlers": ["console"]}
