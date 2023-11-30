import copy
import os
from collections import UserDict
from copy import deepcopy
from functools import cache
from pathlib import Path
from typing import Any

import strictyaml
from loguru import logger

from selva.configuration.defaults import default_settings
from selva.configuration.environment import (
    parse_settings_from_env,
    replace_variables_recursive,
)

__all__ = ("Settings", "SettingsError", "get_settings")

SETTINGS_DIR_ENV = "SELVA_SETTINGS_DIR"
SETTINGS_FILE_ENV = "SELVA_SETTINGS_FILE"

DEFAULT_SETTINGS_DIR = str(Path("configuration"))
DEFAULT_SETTINGS_FILE = "settings.yaml"

SELVA_PROFILE = "SELVA_PROFILE"


class Settings(UserDict):
    def __init__(self, data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = Settings(value)

        super().__init__(data)

    def __getattr__(self, item: str):
        try:
            return self.data[item]
        except KeyError:
            raise AttributeError(item)

    def __copy__(self):
        return Settings(copy.copy(self.data))

    def __deepcopy__(self, memodict):
        data = copy.deepcopy(self.data, memodict)
        return Settings(data)


class SettingsError(Exception):
    def __init__(self, path: Path):
        super().__init__(f"cannot load settings from {path}")
        self.path = path


@cache
def get_settings() -> Settings:
    return _get_settings_nocache()


def _get_settings_nocache() -> Settings:
    # get default settings
    settings = deepcopy(default_settings)

    # merge with main settings file (settings.yaml)
    merge_recursive(settings, get_settings_for_profile())

    # merge with environment settings file (settings_$SELVA_PROFILE.yaml)
    if active_profile := os.getenv(SELVA_PROFILE):
        merge_recursive(settings, get_settings_for_profile(active_profile))

    # merge with environment variables (SELVA_*)
    from_env_vars = parse_settings_from_env(os.environ)
    merge_recursive(settings, from_env_vars)

    settings = replace_variables_recursive(settings, os.environ)
    return Settings(settings)


def get_settings_for_profile(profile: str = None) -> dict[str, Any]:
    settings_file = os.getenv(SETTINGS_FILE_ENV, DEFAULT_SETTINGS_FILE)
    settings_dir_path = Path(os.getenv(SETTINGS_DIR_ENV, DEFAULT_SETTINGS_DIR))
    settings_file_path = settings_dir_path / settings_file

    if profile:
        settings_file_path = settings_file_path.with_stem(
            f"{settings_file_path.stem}_{profile}"
        )

    settings_file_path = settings_file_path.absolute()

    try:
        settings_yaml = settings_file_path.read_text("utf-8")
        logger.debug("settings loaded from {}", settings_file_path)
        return strictyaml.dirty_load(settings_yaml, allow_flow_style=True).data or {}
    except FileNotFoundError:
        if profile:
            logger.warning(
                "no settings file found for profile '{}' at {}",
                profile,
                settings_file_path,
            )

        return {}
    except Exception as err:
        raise SettingsError(settings_file_path) from err


def merge_recursive(destination: dict, source: dict):
    for key in source:
        if key in destination and all(
            isinstance(arg[key], dict) for arg in (destination, source)
        ):
            merge_recursive(destination[key], source[key])
        else:
            destination[key] = deepcopy(source[key])
