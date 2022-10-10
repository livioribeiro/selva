from selva.logging import get_logger


class Test:
    def __init__(self):
        self.logger = get_logger()


print(Test().logger.name)
