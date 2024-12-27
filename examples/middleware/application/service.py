import os
from typing import NamedTuple

from selva.di import service

DEFAULT_NAME = "World"


class Config(NamedTuple):
    default_name: str


@service
def settings_factory() -> Config:
    default_name = os.getenv("DEFAULT_NAME", DEFAULT_NAME)
    return Config(default_name)


class Greeter:
    def __init__(self, config: Config):
        self.config = config

    @property
    def default_name(self):
        return self.config.default_name

    def greet(self, name: str = None):
        greeted_name = name or self.default_name
        return f"Hello, {greeted_name}!"


@service
async def greeter_factory(locator) -> Greeter:
    config = await locator.get(Config)
    return Greeter(config)
