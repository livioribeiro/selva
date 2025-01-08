import copy

import pytest

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.ext.error import ExtensionMissingInitFunctionError, ExtensionNotFoundError
from selva.web.application import Selva


async def test_non_existent_extension_should_fail():
    settings = Settings(
        copy.copy(default_settings)
        | {
            "application": f"{__package__}.application",
            "extensions": ["does.not.exist"],
        }
    )

    app = Selva(settings)

    with pytest.raises(ExtensionNotFoundError):
        await app._lifespan_startup()


async def test_extension_missing_init_function_should_fail():
    settings = Settings(
        copy.copy(default_settings)
        | {
            "application": f"{__package__}.application",
            "extensions": [f"{__package__}.extension"],
        }
    )

    app = Selva(settings)

    with pytest.raises(ExtensionMissingInitFunctionError):
        await app._lifespan_startup()
