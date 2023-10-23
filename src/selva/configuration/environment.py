import copy
import os
import re

RE_VARIABLE = re.compile(r"\$\{(?P<name>\w+?)(?::(?P<default>.*?))?}")


def replace_environment(input_yaml: str):
    input = copy.copy(input_yaml)

    for match in RE_VARIABLE.finditer(input):
        name = match.group("name")
        if value := os.getenv(name):
            input = input.replace(match.group(), value)
            continue
        if value := match.group("default"):
            input = input.replace(match.group(), value)
            continue
        else:
            raise ValueError(f"{name} environment variable is neither defined not contains default value")

    return input