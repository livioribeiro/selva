import os
from typing import NamedTuple

from selva.di import service

DEFAULT_NAME = "World"


class Settings(NamedTuple):
    default_name: str


@service
def settings_factory() -> Settings:
    default_name = os.getenv("DEFAULT_NAME", DEFAULT_NAME)
    return Settings(default_name)


@service
class Greeter:
    def __init__(self, settings: Settings):
        self.default_name = settings.default_name

    def greet(self, name: str = None):
        greeted_name = name or self.default_name
        return f"Hello, {greeted_name}!"
