from asgikit.requests import Request
from httpx import AsyncClient, ASGITransport

from asgikit.requests import Request

from selva.configuration import Settings
from selva.configuration.defaults import default_settings
from selva.web.application import Selva


async def my_middleware(callnext, request: Request):
    async def send(f, event: dict):
        if event["type"] == "http.response.body":
            event["body"] = b"Middleware Ok"
        await f(event)

    request.wrap_asgi(send=send)
    await callnext(request)


async def test_middleware():
    settings = Settings(
        default_settings
        | {
            "application": f"{__package__}.application",
            "middleware": [f"{__package__}.test_middleware.my_middleware"],
        }
    )
    app = Selva(settings)
    await app._lifespan_startup()

    client = AsyncClient(transport=ASGITransport(app=app))
    response = await client.get("http://localhost:8000/")
    assert response.text == "Middleware Ok"
