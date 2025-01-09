import copy

from httpx import ASGITransport, AsyncClient

from selva.configuration import Settings
from selva.configuration.defaults import default_settings
from selva.web.application import Selva

from .application import DerivedException, MyBaseException, MyException

SETTINGS = Settings(
    default_settings
    | {
        "application": f"{__package__}.application",
    }
)


async def test_exception_handler():
    settings = copy.copy(SETTINGS)

    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")
    assert response.json() == {"exception": MyException.__name__}


async def test_derived_exception_handler():
    settings = copy.copy(SETTINGS)

    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))

    response = await client.get("http://localhost:8000/base")
    assert response.text == f"handler=base; exception={MyBaseException.__name__}"

    response = await client.get("http://localhost:8000/derived")
    assert response.text == f"handler=base; exception={DerivedException.__name__}"
