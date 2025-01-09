from selva._util import dotenv
from selva.configuration.settings import get_settings
from selva.di.container import Container
from selva.web.application import Selva

dotenv.init()

settings = get_settings()
di_container = Container()

app = Selva(settings, di_container)
