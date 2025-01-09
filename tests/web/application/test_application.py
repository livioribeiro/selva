from http import HTTPStatus

from httpx import ASGITransport, AsyncClient

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.application import Selva


async def test_application():
    settings = Settings(
        default_settings | {"application": f"{__package__}.application"}
    )
    app = Selva(settings)

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")
    assert response.text == "Ok"


async def test_not_found():
    settings = Settings(
        default_settings | {"application": f"{__package__}.application"}
    )
    app = Selva(settings)

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/not-found")
    assert response.status_code == HTTPStatus.NOT_FOUND
