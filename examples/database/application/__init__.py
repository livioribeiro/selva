import sys

from loguru import logger

logger.remove()
logger.enable("selva")
logger.disable("databases")
logger.disable("aiosqlite")
logger.add(sys.stderr, level="DEBUG")
