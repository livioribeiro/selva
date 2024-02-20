from importlib.util import find_spec

from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.web.templates import Template


async def selva_extension(container: Container, settings: Settings):
    if find_spec("jinja2") is None:
        raise ModuleNotFoundError("Missing 'jinja2'. Install 'selva' with 'jinja' extra.")

    backend = settings.templates.backend

    if backend and backend != "jinja":
        return

    if not backend and (current := await container.get(Template, optional=True)):
        cls = current.__class__
        current_class = f"{cls.__module__}.{cls.__qualname__}"

        raise ValueError(
            f"Template backend already registered with '{current_class}'. "
            "Please define `templates.backend` property."
        )

    container.scan(f"{__package__}.service")
