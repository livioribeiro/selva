import os
from typing import Annotated, NamedTuple

from selva.di import Inject, service

DEFAULT_NAME = "World"


class Settings(NamedTuple):
    default_name: str


@service
def settings_factory() -> Settings:
    default_name = os.getenv("DEFAULT_NAME", DEFAULT_NAME)
    return Settings(default_name)


@service
class Greeter:
    settings: Annotated[Settings, Inject]

    @property
    def default_name(self):
        return self.settings.default_name

    def greet(self, name: str = None):
        greeted_name = name or self.default_name
        return f"Hello, {greeted_name}!"
