from importlib.util import find_spec

from selva.conf.settings import Settings
from selva.di.container import Container
from selva.ext.templates.mako.service import MakoTemplate, template_lookup

__all__ = ("MakoTemplate",)


async def init_extension(container: Container, _settings: Settings):
    if find_spec("mako") is None:
        raise ModuleNotFoundError("Missing 'mako'. Install 'selva' with 'mako' extra.")

    container.register(template_lookup)
    container.register(MakoTemplate)
