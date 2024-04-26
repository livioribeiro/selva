import copy

from loguru import logger

from selva._util.import_item import import_item
from selva.configuration.settings import Settings
from selva.logging.stdlib import setup_loguru_std_logging_interceptor

_IMPORT_PROPS = ["sink", "format", "filter", "patcher"]


def setup_logging(settings: Settings):
    config = copy.deepcopy(settings.logging.config) if settings.logging.config else {}

    handlers = enumerate(config.get("handlers", []))

    for i, handler in handlers:
        for prop in _IMPORT_PROPS:
            if (item := handler.get(prop)) and isinstance(item, str) and item.startswith("ext://"):
                config.handlers[i][prop] = import_item(item.removeprefix("ext://"))

    logger.configure(**config)

    setup_loguru_std_logging_interceptor()
