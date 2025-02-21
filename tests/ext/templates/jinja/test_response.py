from pathlib import Path

from httpx import ASGITransport, AsyncClient

from selva.conf.defaults import default_settings
from selva.conf.settings import Settings
from selva.web.application import Selva

path = str((Path(__file__).parent / "templates").absolute())
settings = Settings(
    default_settings
    | {
        "application": f"{__package__}.application",
        "extensions": ["selva.ext.templates.jinja"],
        "templates": {"jinja": {"paths": [path]}},
    }
)


async def test_render():
    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/render")

    assert response.status_code == 200
    assert response.text == "Jinja"
    assert response.headers["Content-Length"] == str(len("Jinja"))
    assert "text/html" in response.headers["Content-Type"]


async def test_stream():
    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/stream")

    assert response.status_code == 200
    assert response.text == "Jinja"
    assert "Content-Length" not in response.headers


async def test_content_type():
    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/content_type")

    assert response.status_code == 200
    assert response.text == "Jinja"
    assert response.headers["Content-Length"] == str(len("Jinja"))
    assert "text/plain" in response.headers["Content-Type"]
