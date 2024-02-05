from http import HTTPStatus

from httpx import AsyncClient

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.application import Selva


async def test_application():
    settings = Settings(
        default_settings | {
            "application": "tests.contrib.data.sqlalchemy.application",
            "data": {
                "sqlalchemy": {
                    "default": {
                        "url": "sqlite+aiosqlite:///:memory:"
                    }
                }
            }
        }
    )

    app = Selva(settings)

    await app._lifespan_startup()

    client = AsyncClient(app=app)
    response = await client.get("http://localhost:8000/")

    assert response.status_code == HTTPStatus.OK
