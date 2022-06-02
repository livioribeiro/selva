from dataclasses import dataclass

from selva.di import service


@service
class Dependency:
    pass


@service
@dataclass
class ServiceDataclass:
    dependency: Dependency
