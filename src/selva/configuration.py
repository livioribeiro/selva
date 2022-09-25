import importlib
import importlib.util
import inspect
import os
import warnings
from pathlib import Path
from typing import Any
from types import ModuleType, SimpleNamespace

__all__ = ("Settings",)

SELVA_SETTINGS_MODULE = "SELVA_SETTINGS_MODULE"
DEFAULT_SELVA_SETTINGS_MODULE = "configuration.settings"

SELVA_ENV = "SELVA_ENV"


def is_valid_conf(conf: str) -> bool:
    """Checks if the config item can be collected into settings

    Config settings that are exported must start with an uppercase letter
    followed by other uppercase letters, numbers or underscores
    """

    if not (conf[0].isalpha() and conf[0].isupper()):
        return False

    return all(
        (i.isalpha() and i.isupper()) or i.isnumeric() or i == "_"
        for i in conf
    )


def extract_valid_keys(settings: ModuleType) -> dict[str, Any]:
    """Collect settings from module into dict"""
    return {
        name: value
        for name, value in inspect.getmembers(settings)
        if is_valid_conf(name)
    }


def get_settings_for_env(env: str = None) -> dict[str, Any]:
    settings_module_path = os.getenv(SELVA_SETTINGS_MODULE, DEFAULT_SELVA_SETTINGS_MODULE)

    if env is not None:
        settings_module_path += f"_{env}"

    try:
        settings_module = importlib.import_module(settings_module_path)
    except ImportError:
        warnings.warn(f"settings module not found: {settings_module_path}")
        return {}

    return extract_valid_keys(settings_module)


def get_settings() -> dict[str, Any]:
    settings = get_settings_for_env()

    if active_env := os.getenv(SELVA_ENV):
        env_settings = get_settings_for_env(active_env)
        settings |= env_settings

    return settings


class Settings(SimpleNamespace):
    def __init__(self):
        super().__init__(**get_settings())
