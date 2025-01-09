from copy import deepcopy
from pathlib import Path

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.ext.templates.jinja.service import JinjaTemplate


async def test_render_template():
    path = str(Path(__file__).parent.absolute())
    settings = Settings(default_settings | {"templates": {"jinja": {"paths": [path]}}})

    template = JinjaTemplate(settings)
    template.initialize()
    result = await template.render("template.html", {"variable": "Jinja"})
    assert result == "Jinja"


async def test_render_str():
    settings = Settings(deepcopy(default_settings))
    template = JinjaTemplate(settings)
    template.initialize()
    result = await template.render_str("{{ variable }}", {"variable": "Jinja"})
    assert result == "Jinja"
