from selva._util import dotenv
from selva.configuration.settings import get_settings
from selva.web.application import Selva

dotenv.init()
settings = get_settings()
app = Selva(settings)
