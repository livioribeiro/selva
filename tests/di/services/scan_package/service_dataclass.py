from dataclasses import dataclass

from selva.di import singleton


@singleton
class Dependency:
    pass


@singleton
@dataclass
class ServiceDataclass:
    dependency: Dependency
