import copy
import logging
import logging.config

from selva.configuration.settings import Settings

__all__ = ("setup_logging", "build_logging_config")

logger = logging.getLogger(__name__)


def build_logging_config(
    logging_config: dict, loglevel_config: dict[str, str | dict[str, str]]
) -> dict:
    config = copy.deepcopy(logging_config)

    if "loggers" not in config:
        config["loggers"] = {}

    # get first handler or empty list
    handlers = list(config["handlers"].keys())[:1]

    for name, level in loglevel_config.items():
        if name not in config["loggers"]:
            config["loggers"][name] = {
                "level": "NOTSET",
                "handlers": handlers,
            }

        if isinstance(level, str):
            config["loggers"][name]["level"] = level
        elif isinstance(level, dict):
            config["loggers"][name] = level
        else:
            raise ValueError(
                f"logging level config must be str or dict, '{repr(type(level))}' given"
            )

    return config


def setup_logging(settings: Settings):
    new_config = build_logging_config(settings.LOGGING, settings.LOGGING_LEVEL)
    settings.LOGGING = new_config
    logging.config.dictConfig(settings.LOGGING)
    logger.info("Logging config: %s", repr(settings.LOGGING))
