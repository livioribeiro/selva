import os
from typing import Annotated, NamedTuple

from selva.di import Inject, service

DEFAULT_NAME = "World"


class Config(NamedTuple):
    default_name: str


@service
def settings_factory() -> Config:
    default_name = os.getenv("DEFAULT_NAME", DEFAULT_NAME)
    return Config(default_name)


@service
class Greeter:
    config: Annotated[Config, Inject]

    @property
    def default_name(self):
        return self.config.default_name

    def greet(self, name: str = None):
        greeted_name = name or self.default_name
        return f"Hello, {greeted_name}!"
