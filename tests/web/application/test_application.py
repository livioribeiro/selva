import sys
from pathlib import Path

from httpx import AsyncClient

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.application import Selva


async def test_application():
    settings = Settings(default_settings | {
        "components": ["tests.web.application.application"]
    })
    app = Selva(settings)

    client = AsyncClient(app=app)
    response = await client.get("http://localhost:8000/")
    assert response.text == "Selva"
