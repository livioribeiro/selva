from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.application import Selva
from selva.web.lifecycle.decorator import startup


@startup
def startup():
    print("startup", end="")


async def test_application(capfd):
    settings = Settings(
        default_settings
        | {
            "application": f"{test_application.__module__}",
        }
    )

    app = Selva(settings)

    await app._lifespan_startup()
    assert capfd.readouterr().out == "startup"
