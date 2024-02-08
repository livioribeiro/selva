from http import HTTPStatus

import pytest
from httpx import AsyncClient

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.application import Selva


@pytest.mark.parametrize(
    "application,database",
    [
        ("application", "default"),
        ("application_named", "other"),
    ],
    ids=["default", "named"],
)
async def test_application(application: str, database: str):
    settings = Settings(
        default_settings
        | {
            "application": f"{__package__}.{application}",
            "extensions": ["selva.ext.data.sqlalchemy"],
            "data": {"sqlalchemy": {database: {"url": "sqlite+aiosqlite:///:memory:"}}},
        }
    )

    app = Selva(settings)

    await app._lifespan_startup()

    client = AsyncClient(app=app)
    response = await client.get("http://localhost:8000/")

    assert response.status_code == HTTPStatus.OK
