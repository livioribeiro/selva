from copy import deepcopy
from pathlib import Path

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.ext.templates.mako.service import MakoTemplate


async def test_render_template():
    path = str(Path(__file__).parent.absolute())
    settings = Settings(
        default_settings | {"templates": {"mako": {"directories": [path]}}}
    )

    template = MakoTemplate(settings)
    template.initialize()
    result = await template.render("template.html", {"variable": "Mako"})
    assert result == "Mako"


async def test_render_str():
    settings = Settings(deepcopy(default_settings))
    template = MakoTemplate(settings)
    template.initialize()
    result = await template.render_str("${variable}", {"variable": "Mako"})
    assert result == "Mako"
