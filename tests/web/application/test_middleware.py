from asgikit.requests import Request
from httpx import AsyncClient

from selva.configuration import Settings
from selva.configuration.defaults import default_settings
from selva.di import service
from selva.web.application import Selva


@service
class MyMiddleware:
    async def __call__(self, call, request):
        send = request.asgi.send

        async def new_send(event: dict):
            if event["type"] == "http.response.body":
                event["body"] = b"Middleware Ok"
            await send(event)

        new_request = Request(request.asgi.scope, request.asgi.receive, new_send)
        await call(new_request)


async def test_middleware():
    settings = Settings(
        default_settings
        | {
            "application": f"{__package__}.application",
            "middleware": [f"{__package__}.test_middleware.MyMiddleware"],
        }
    )
    app = Selva(settings)
    app.di.register(MyMiddleware)
    await app._lifespan_startup()

    client = AsyncClient(app=app)
    response = await client.get("http://localhost:8000/")
    assert response.text == "Middleware Ok"
