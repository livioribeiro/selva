from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.web.templates import Template

from loguru import logger


def selva_extension(container: Container, settings: Settings):
    backend = settings.templates.backend

    if backend and backend != __package__:
        return

    if not backend and container.has(Template):
        raise ValueError("Template backend already registered. Please define `templates.backend` property")

    from . import service
    container.scan(service)
