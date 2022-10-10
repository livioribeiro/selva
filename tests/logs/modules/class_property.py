from selva.logging import get_logger


class Test:
    logger = get_logger()


print(Test.logger.name)
