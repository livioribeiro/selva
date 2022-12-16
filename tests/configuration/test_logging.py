import logging

from selva.configuration.logging import setup_logging
from selva.configuration.settings import Settings


# def test_logging_config_is_logged(caplog):
#     caplog.set_level(logging.DEBUG, logger="selva")
#     setup_logging(Settings())
#
#     assert "Logging config: " in caplog.text