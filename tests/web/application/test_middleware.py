from httpx import ASGITransport, AsyncClient

from selva.configuration import Settings
from selva.configuration.defaults import default_settings
from selva.web.application import Selva


def my_middleware(app, settings, di):
    async def inner(scope, receive, send):
        async def new_send(event: dict):
            if event["type"] == "http.response.body":
                event["body"] = b"Middleware Ok"
            await send(event)

        await app(scope, receive, new_send)

    return inner


async def test_middleware():
    settings = Settings(
        default_settings
        | {
            "application": f"{__package__}.application",
            "middleware": [f"{__package__}.test_middleware:my_middleware"],
        }
    )
    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")
    assert response.text == "Middleware Ok"
