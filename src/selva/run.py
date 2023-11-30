import os

from dotenv import load_dotenv

from selva.configuration.settings import get_settings
from selva.web.application import Selva

dotenv_path = os.getenv("SELVA_DOTENV", os.path.join(os.getcwd(), ".env"))
load_dotenv(dotenv_path)

settings = get_settings()
app = Selva(settings)
