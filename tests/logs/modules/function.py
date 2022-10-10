from selva.logging import get_logger


def func():
    logger = get_logger()
    print(logger.name)


func()
