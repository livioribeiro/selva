from selva.configuration import Settings
from selva.di import Inject
from selva.web import controller, get


@controller
class Controller:
    settings: Settings = Inject()

    @get
    def index(self) -> str:
        return self.settings.MESSAGE
