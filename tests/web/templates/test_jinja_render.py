from pathlib import Path

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.templates.jinja import JinjaTemplate


async def test_render_template():
    path = str(Path(__file__).parent.absolute())
    settings = Settings(default_settings | {"templates": {"jinja": {"path": path}}})

    template = JinjaTemplate(settings)
    template.initialize()
    result = await template.render("template.html", {"variable": "Jinja"})
    assert result == "Jinja"


async def test_render_str():
    settings = Settings(default_settings)
    template = JinjaTemplate(settings)
    template.initialize()
    result = await template.render_str("{{ variable }}", {"variable": "Jinja"})
    assert result == "Jinja"
