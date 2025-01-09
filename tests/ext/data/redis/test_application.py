import os
from http import HTTPStatus

import pytest
from httpx import ASGITransport, AsyncClient

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.application import Selva

REDIS_URL = os.environ.get("REDIS_URL")


@pytest.mark.skipif(REDIS_URL is None, reason="REDIS_URL not set")
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
            "extensions": ["selva.ext.data.redis"],
            "data": {"redis": {database: {"url": REDIS_URL}}},
        }
    )

    app = Selva(settings)

    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")

    await app._lifespan_shutdown()

    assert response.status_code == HTTPStatus.OK
