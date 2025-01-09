from importlib.util import find_spec

from selva.configuration.settings import Settings
from selva.di.container import Container
from selva.ext.templates.jinja.service import JinjaTemplate

__all__ = ("JinjaTemplate",)


async def init_extension(container: Container, _settings: Settings):
    if find_spec("jinja2") is None:
        raise ModuleNotFoundError(
            "Missing 'jinja2'. Install 'selva' with 'jinja' extra."
        )

    container.register(JinjaTemplate)
