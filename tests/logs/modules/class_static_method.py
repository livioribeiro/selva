from selva.logging import get_logger


class Test:
    @staticmethod
    def test():
        logger = get_logger()
        print(logger.name)


Test.test()
