import sys
from functools import cache

from loguru import logger

from selva.configuration.settings import Settings
from selva.logging.stdlib import setup_loguru_std_logging_interceptor


def setup_logger(settings: Settings):
    enable = [(name, True) for name in settings.logging.enable]
    disable = [(name, False) for name in settings.logging.disable]

    # enabling has precedence over disabling
    # therefore the "enable" list comes after the "disable" list
    activation = disable + enable

    log_config = settings.get("logging", {})
    root_level = logger.level(log_config.get("root", "WARNING"))
    log_level = {
        name: logger.level(value) for name, value in log_config.get("level", {}).items()
    }

    filter_func = filter_func_factory(root_level, log_level)
    handler = {"sink": sys.stderr, "filter": filter_func}

    logger.configure(handlers=[handler], activation=activation)

    setup_loguru_std_logging_interceptor()


def filter_func_factory(root_level, log_level: dict):
    @cache
    def has_level(name: str, record_level):
        level = log_level.get(name)

        while not level:
            match name.rsplit(".", 1):
                case [first, _last]:
                    name = first
                    level = log_level.get(name)
                case _:
                    level = root_level

        return record_level.no >= level.no

    def filter_func(record):
        name = record["name"]
        record_level = record["level"]
        return has_level(name, record_level)

    return filter_func
