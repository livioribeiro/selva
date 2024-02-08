from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.web.templates import Template


async def selva_extension(container: Container, settings: Settings):
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
