from selva.configuration.settings import Settings
from selva.di.container import Container


def selva_extension(container: Container, settings: Settings):
    backends = [key for key in settings.templates if key != "backend"]
    if backends != ["jinja"] and settings.templates.backend != "jinja":
        return

    from . import service

    container.scan(service)
