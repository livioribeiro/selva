import os

from dotenv import load_dotenv

__all__ = ("init",)


def init():
    dotenv_path = os.getenv("SELVA_DOTENV", os.path.join(os.getcwd(), ".env"))
    load_dotenv(dotenv_path)
