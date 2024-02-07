from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.web.application import Selva


async def test_extension():
    settings = Settings(
        default_settings
        | {
            "application": "tests.ext.register_extension.application",
            "extensions": ["tests.ext.register_extension.extension"],
        }
    )

    app = Selva(settings)

    await app._lifespan_startup()

    assert settings.tested
