from pathlib import Path

from httpx import ASGITransport, AsyncClient

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.application import Selva

path = str(Path(__file__).parent.absolute())
settings = Settings(
    default_settings
    | {
        "application": f"{__package__}.application",
        "extensions": ["selva.ext.templates.mako"],
        "templates": {"mako": {"directories": [path]}},
    }
)


async def test_render():
    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/render")

    assert response.status_code == 200
    assert response.text == "Mako"
    assert response.headers["Content-Length"] == str(len("Mako"))
    assert "text/html" in response.headers["Content-Type"]


async def test_define_content_type():
    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/define_content_type")

    assert response.status_code == 200
    assert "text/defined" in response.headers["Content-Type"]


async def test_override_content_type():
    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/override_content_type")

    assert response.status_code == 200
    assert "text/overriden" in response.headers["Content-Type"]


async def test_content_type_from_response():
    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/content_type_from_response")

    assert response.status_code == 200
    assert "text/from_response" in response.headers["Content-Type"]
