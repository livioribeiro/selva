import os

from selva.web import Application, controller, get
from selva.web.configuration import Settings


@controller
class Controller:
    def __init__(self, settings: Settings):
        self.settings = settings

    @get
    def index(self) -> str:
        return self.settings.get("message")


# os.putenv("SELVA_ENV", "dev")

app = Application(Controller)
