from selva.web import Selva, controller, get
from selva.configuration import Settings


@controller
class Controller:
    def __init__(self, settings: Settings):
        self.settings = settings

    @get
    def index(self) -> str:
        return self.settings["message"]


app = Selva(Controller)
