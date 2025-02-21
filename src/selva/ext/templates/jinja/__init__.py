from importlib.util import find_spec


from selva.conf.settings import Settings
from selva.di.container import Container
from selva.ext.templates.jinja.service import JinjaTemplate, jinja_environment


async def init_extension(container: Container, _settings: Settings):
    if find_spec("jinja2") is None:
        raise ModuleNotFoundError(
            "Missing 'jinja2'. Install 'selva' with 'jinja' extra."
        )

    container.register(jinja_environment)
    container.register(JinjaTemplate)
