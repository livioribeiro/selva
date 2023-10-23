import os
from collections import UserDict
from copy import deepcopy
from pathlib import Path
from typing import Any

import strictyaml
from loguru import logger

from selva.configuration.defaults import default_settings
from selva.configuration.environment import replace_environment

__all__ = ("Settings", "SettingsModuleError", "get_settings")

SELVA_SETTINGS_DIR = "SELVA_SETTINGS_DIR"
DEFAULT_SELVA_SETTINGS_FILE = str(Path("configuration") / "settings.yaml")

SELVA_ENV = "SELVA_ENV"


class SettingsModuleError(Exception):
    def __init__(self, path: Path):
        super().__init__(f"cannot load settings module: {path}")
        self.path = path


def get_settings_for_env(env: str = None) -> dict[str, Any]:
    settings_file_name = "settings"

    settings_file_path = Path(
        os.getenv(SELVA_SETTINGS_DIR, DEFAULT_SELVA_SETTINGS_FILE)
    )

    if env is not None:
        settings_file_name += f"_{env}"
        settings_file_path = settings_file_path.with_stem(
            f"{settings_file_path.stem}_{env}"
        )

    settings_file_path = settings_file_path.absolute()

    try:
        settings_yaml = settings_file_path.read_text("utf-8")
        settings_yaml = replace_environment(settings_yaml)
        return strictyaml.load(settings_yaml).data
    except FileNotFoundError:
        logger.info("settings file not found: {}", settings_file_path)
        return {}
    except (KeyError, ValueError):
        raise
    except Exception as err:
        raise SettingsModuleError(settings_file_path) from err


class Settings(UserDict):
    pass


def _merge_settings(arg1: dict, arg2: dict):
    for key in arg2:
        if key in arg1 and all(isinstance(arg[key], dict) for arg in (arg1, arg2)):
            _merge_settings(arg1[key], arg2[key])
        else:
            arg1[key] = arg2[key]


def get_settings() -> Settings:
    settings = deepcopy(default_settings)
    _merge_settings(settings, get_settings_for_env())

    if active_env := os.getenv(SELVA_ENV):
        _merge_settings(settings, get_settings_for_env(active_env))

    return Settings(settings)
