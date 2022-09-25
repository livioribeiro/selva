import importlib
import importlib.util
import inspect
import os
import warnings
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

__all__ = ("Settings",)

SELVA_SETTINGS_MODULE = "SELVA_SETTINGS_MODULE"
DEFAULT_SELVA_SETTINGS_MODULE = "configuration/settings.py"

SELVA_ENV = "SELVA_ENV"


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


def get_settings_for_env(env: str = None) -> dict[str, Any]:
    settings_module_path = Path(
        os.getenv(SELVA_SETTINGS_MODULE, DEFAULT_SELVA_SETTINGS_MODULE)
    )
    settings_module_path = settings_module_path.with_suffix(".py")

    if env is not None:
        settings_module_path = settings_module_path.with_stem(
            f"{settings_module_path.stem}_{env}"
        )

    settings_module_path = settings_module_path.absolute()

    try:
        spec = importlib.util.spec_from_file_location(
            "selva_settings", settings_module_path
        )
        settings_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings_module)
    except FileNotFoundError:
        # TODO: write tests
        warnings.warn(f"settings module not found: {settings_module_path}")
        return {}
    except ImportError:
        # TODO: find out what to do
        # TODO: write tests
        raise

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
