import pytest
from httpx import ASGITransport, AsyncClient

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.application import Selva


async def test_application():
    settings = Settings(
        default_settings
        | {
            "application": f"{__package__}.application_scoped_session",
            "extensions": ["selva.ext.data.sqlalchemy"],
            "middleware": [
                "selva.ext.data.sqlalchemy.middleware.scoped_session"
            ],
            "data": {
                "sqlalchemy": {
                    "connections": {"default": {"url": "sqlite+aiosqlite:///:memory:"}}
                }
            },
        }
    )

    app = Selva(settings)

    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")

    assert response.text == "1"


async def test_scoped_session_outside_request_should_fail():
    settings = Settings(
        default_settings
        | {
            "application": f"{__package__}.application_scoped_session_startup",
            "extensions": ["selva.ext.data.sqlalchemy"],
            "middleware": [
                "selva.ext.data.sqlalchemy.middleware.scoped_session"
            ],
            "data": {
                "sqlalchemy": {
                    "connections": {"default": {"url": "sqlite+aiosqlite:///:memory:"}}
                }
            },
        }
    )

    app = Selva(settings)

    with pytest.raises(RuntimeError, match="ScopedSession outside request"):
        await app._lifespan_startup()
