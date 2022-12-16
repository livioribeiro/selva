import importlib
import importlib.util
import inspect
import logging
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

from . import defaults

__all__ = ("Settings", "SettingsModuleError")

SELVA_SETTINGS_MODULE = "SELVA_SETTINGS_MODULE"
DEFAULT_SELVA_SETTINGS_MODULE = str(Path("configuration") / "settings.py")

SELVA_ENV = "SELVA_ENV"

logger = logging.getLogger(__name__)


class SettingsModuleError(Exception):
    def __init__(self, path: Path):
        super().__init__(f"cannot load settings module: {path}")
        self.path = path


def is_valid_conf(conf: str) -> bool:
    """Checks if the config item can be collected into settings

    Config settings that are exported must start with an uppercase letter
    followed by other uppercase letters, numbers or underscores
    """

    if not (conf[0].isalpha() and conf[0].isupper()):
        return False

    return all((i.isalpha() and i.isupper()) or i.isnumeric() or i == "_" for i in conf)


def extract_valid_keys(settings: ModuleType) -> dict[str, Any]:
    """Collect settings from module into dict"""
    return {
        name: value
        for name, value in inspect.getmembers(settings)
        if is_valid_conf(name)
    }


def get_default_settings():
    return extract_valid_keys(defaults)


def get_settings_for_env(env: str = None) -> dict[str, Any]:
    settings_module_name = "selva_settings"

    settings_module_path = Path(
        os.getenv(SELVA_SETTINGS_MODULE, DEFAULT_SELVA_SETTINGS_MODULE)
    )
    settings_module_path = settings_module_path.with_suffix(".py")

    if env is not None:
        settings_module_name += f"_{env}"
        settings_module_path = settings_module_path.with_stem(
            f"{settings_module_path.stem}_{env}"
        )

    settings_module_path = settings_module_path.absolute()

    try:
        spec = importlib.util.spec_from_file_location(
            settings_module_name, settings_module_path
        )
        settings_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings_module)
    except FileNotFoundError:
        logger.info("settings module not found: %s", settings_module_path)
        return {}
    except Exception as err:
        raise SettingsModuleError(settings_module_path) from err

    return extract_valid_keys(settings_module)


def get_settings() -> dict[str, Any]:
    settings = get_default_settings()

    settings |= get_settings_for_env()

    if active_env := os.getenv(SELVA_ENV):
        settings |= get_settings_for_env(active_env)

    return settings


class Settings(SimpleNamespace):
    def __init__(self):
        super().__init__(**get_settings())

    def get(self, name: str, default=None) -> Any | None:
        return getattr(self, name, default)
