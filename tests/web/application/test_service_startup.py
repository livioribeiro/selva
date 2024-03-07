from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.di import service
from selva.web.application import Selva


async def test_application():
    @service(startup=True)
    class Service:
        startup_called = False

        def initialize(self):
            Service.startup_called = True

    settings = Settings(
        default_settings | {
            "application": f"{__package__}.application",
        }
    )

    app = Selva(settings)
    app.di.register(Service)

    await app._lifespan_startup()

    assert Service.startup_called
