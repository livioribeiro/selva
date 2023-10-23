from loguru import logger

from selva.logging.stdlib import setup_loguru_std_logging_interceptor

# disable asgikit and selva loggers by default
logger.disable("asgikit")
logger.disable("selva")

setup_loguru_std_logging_interceptor()
