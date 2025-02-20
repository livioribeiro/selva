from importlib.util import find_spec

import jinja2

from selva.conf.settings import Settings
from selva.di.container import Container
from selva.ext.templates.jinja.service import get_template_services, jinja_environment


async def init_extension(container: Container, settings: Settings):
    if find_spec("jinja2") is None:
        raise ModuleNotFoundError(
            "Missing 'jinja2'. Install 'selva' with 'jinja' extra."
        )

    environment = jinja_environment(settings)
    container.define(jinja2.Environment, environment)

    for tpl in get_template_services(environment):
        container.register(tpl)
