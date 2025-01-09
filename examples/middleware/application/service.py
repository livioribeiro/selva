import os
from functools import cached_property
from typing import Annotated as A
from typing import NamedTuple

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
    config: A[Config, Inject]

    @cached_property
    def default_name(self):
        return self.config.default_name

    def greet(self, name: str = None):
        greeted_name = name or self.default_name
        return f"Hello, {greeted_name}!"
