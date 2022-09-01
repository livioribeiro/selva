from selva.web import Selva, controller, get
from selva.web.configuration import Settings


@controller
class Controller:
    def __init__(self, settings: Settings):
        self.settings = settings

    @get
    def index(self) -> str:
        return self.settings.get("message")


app = Selva(Controller)
