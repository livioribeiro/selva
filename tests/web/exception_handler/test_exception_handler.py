from httpx import AsyncClient, ASGITransport

from selva.configuration import Settings
from selva.configuration.defaults import default_settings
from selva.web.application import Selva

from .application import MyException


async def test_exception_handler():
    settings = Settings(
        default_settings
        | {
            "application": f"{__package__}.application",
        }
    )

    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")
    assert response.json() == {"exception": MyException.__name__}
