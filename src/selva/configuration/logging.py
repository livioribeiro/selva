import logging
import logging.config

from selva.configuration.settings import Settings

__all__ = ("setup_logging",)

logger = logging.getLogger(__name__)

_DEFAULT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": None,
    "handlers": None,
    "loggers": None,
}


def setup_logging(settings: Settings):
    if not settings.LOGGING:
        settings.LOGGING = _DEFAULT | {
            "formatters": settings.LOGGING_FORMATTERS,
            "handlers": settings.LOGGING_HANDLERS,
            "loggers": settings.LOGGING_LOGGERS,
        }

    logging.config.dictConfig(settings.LOGGING)
    logger.info("Logging config: %s", repr(settings.LOGGING))
