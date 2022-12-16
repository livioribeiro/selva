import logging
import logging.config

from selva.configuration.settings import Settings

logger = logging.getLogger(__name__)


def setup_logging(settings: Settings):
    logging.config.dictConfig(settings.LOGGING)

    logger.info("Logging config: %s", repr(settings.LOGGING))
