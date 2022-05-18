from dataclasses import dataclass

from dependency_injector import singleton


@singleton
class Dependency:
    pass


@singleton
@dataclass
class ServiceDataclass:
    dependency: Dependency
