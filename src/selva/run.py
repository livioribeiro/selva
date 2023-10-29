import os

from dotenv import load_dotenv
from selva.web.application import Selva

dotenv_path = os.getenv("SELVA_DOTENV", os.path.join(os.getcwd(), ".env"))
load_dotenv(dotenv_path)

app = Selva()
