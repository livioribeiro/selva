import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Optional

try:
    import tomllib as toml
except ImportError:
    import tomli as toml


CONFIGURATION_DIR_NAME = "configuration"
RESOURCES_DIR_NAME = "resources"
MAIN_SETTINGS_FILE = "application.toml"
ENV_SETTINGS_FILE = "application-{}.toml"
SELVA_ENV = "SELVA_ENV"
SELVA_ENV_PREFIX = "SELVA_"


def _flatten_dict(source: dict) -> Iterable[tuple[str, Any]]:
    for name, value in source.items():
        if isinstance(value, dict):
            for subname, subvalue in _flatten_dict(value):
                yield f"{name}:{subname}".lower(), subvalue
        else:
            yield name.lower(), value


def flatten_dict(source: dict) -> dict[str, Any]:
    return dict(_flatten_dict(source))


def load_config_file(settings_path: Path) -> dict[str, Any]:
    settings = {}

    if settings_path.exists():
        with settings_path.open("rb") as conf:
            settings = toml.load(conf)

        if include := settings.pop("include", None):
            if isinstance(include, str):
                include = [include]

            if isinstance(include, (list, tuple, set)):
                for include_file in include:
                    include_path = settings_path.parent / include_file
                    include_path = include_path.with_suffix(".toml")

                    if not include_path.exists():
                        raise ValueError(f"{include_path} does not exist")

                    with include_path.open("rb") as conf:
                        settings |= toml.load(conf)
            else:
                raise ValueError("'include' must be string or list")

    return flatten_dict(settings)


def load_config_env() -> dict[str, Any]:
    settings = {}

    for key, value in os.environ.items():
        if not key.startswith("SELVA_"):
            continue

        name = key.removeprefix("SELVA_").lstrip("_").lower().replace("__", ":")
        settings[name] = value

    return settings


def get_settings() -> dict[str, Any]:
    configuration_dir = Path(os.getcwd()) / CONFIGURATION_DIR_NAME
    main_settings_file = configuration_dir / MAIN_SETTINGS_FILE

    settings = load_config_file(main_settings_file)

    if selva_env := os.getenv(SELVA_ENV):
        env_settings_file = configuration_dir / ENV_SETTINGS_FILE.format(selva_env)
        settings |= load_config_file(env_settings_file)

    settings |= load_config_env()

    return settings


class Settings:
    def __init__(self, initial: dict = None):
        self._data = get_settings()
        if initial:
            self._data |= flatten_dict(initial)

    def get(self, *args) -> Any | None:
        key = ":".join(args).lower()
        return self._data.get(key)

    def __getitem__(self, item) -> Any | None:
        if isinstance(item, tuple):
            return self.get(*item)
        return self.get(item)

    @property
    def resources_path(self):
        return Path(os.getcwd()) / "resources"

    def resource_path(self, *args: str):
        resources = self.resources_path
        return resources.joinpath(*args)
