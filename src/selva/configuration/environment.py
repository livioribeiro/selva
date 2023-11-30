import re
from collections.abc import Mapping, Sequence
from typing import Any

RE_VARIABLE = re.compile(
    r"""
        \$\{                        # Expression start with '${'
            \ ?                     # Blank space before variable name
            (?P<name>\w+?)          # Environment variable name
            \ ?                     # Blank space after variable name
            (?:                     # Default value non-capture group
                :                   # Collon separating variable name and default value
                \ ?                 # Blank space before default value
                (?P<default>.*?)    # Default value
                \ ?                 # Blank space after default value
            )?                      # End of default value non-capture group
        }                           # Expression end with '}'
    """,
    re.VERBOSE,
)


SELVA_PREFIX = "SELVA__"


def parse_settings_from_env(source: Mapping[str, str]) -> dict:
    result = {}

    for name, value in source.items():
        if not name.startswith(SELVA_PREFIX):
            continue

        current_ref = result
        keys = name.removeprefix(SELVA_PREFIX).split("__")

        match keys:
            case [key] if key.strip() != "":
                current_key = key.lower()
            case [first_key, *keys, last_key]:
                for key in [first_key] + keys:
                    key = key.lower()
                    if key not in current_ref:
                        current_ref[key] = {}
                    current_ref = current_ref[key]
                current_key = last_key.lower()
            case _:
                continue

        current_ref[current_key] = value

    return result


def replace_variables_with_env(settings: str, environ: Mapping[str, str]):
    for match in RE_VARIABLE.finditer(settings):
        name = match.group("name")

        if value := environ.get(name):
            settings = settings.replace(match.group(), value)
            continue

        if value := match.group("default"):
            settings = settings.replace(match.group(), value)
            continue

        raise ValueError(
            f"{name} environment variable is not defined and does not contain a default value"
        )

    return settings


def replace_variables_recursive(
    data: Mapping | Sequence | str | Any, environ: Mapping[str, str]
):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = replace_variables_recursive(value, environ)
        return data
    elif isinstance(data, list):
        return [replace_variables_recursive(value, environ) for value in data]
    elif isinstance(data, str):
        return replace_variables_with_env(data, environ)
    else:
        return data
