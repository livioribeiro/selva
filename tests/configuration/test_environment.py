from selva.configuration.environment import (
    parse_settings_from_env,
    replace_variables_recursive,
    replace_variables_with_env,
)


def test_parse_settings():
    source = {
        "SELVA__ENV1": "1",
        "SELVA__PATH1__ENV2": "2",
        "SELVA__PATH1__PATH2__SUB_ENV3": "3",
        "SELVA__PATH1__PATH2__SUB_ENV4": "4",
        "SELVA__": "None",
        "NOT_SELVA_ENV": "None",
    }

    result = parse_settings_from_env(source)

    expected = {
        "env1": "1",
        "path1": {
            "env2": "2",
            "path2": {
                "sub_env3": "3",
                "sub_env4": "4",
            },
        },
    }
    assert result == expected


def test_replace_variable_from_environ():
    yaml = "${VAR}"
    result = replace_variables_with_env(yaml, {"VAR": "value"})

    assert result == "value"


def test_replace_variable_from_default():
    yaml = "${VAR:default}"
    result = replace_variables_with_env(yaml, {})

    assert result == "default"


def test_replace_variable_environ_precedence():
    yaml = "${VAR:default}"
    result = replace_variables_with_env(yaml, {"VAR": "value"})

    assert result == "value"


def test_replace_multiple_variables():
    yaml = "${VAR1} ${VAR2}"
    result = replace_variables_with_env(yaml, {"VAR1": "1", "VAR2": "2"})

    assert result == "1 2"


def test_replace_variables_recursive():
    settings = {
        "prop": "${VAR1}",
        "list": ["${VAR2}"],
        "dict": {
            "var": "${VAR3}",
            "subdict": {"var": "${VAR4}"},
        },
    }

    environ = {"VAR1": "1", "VAR2": "2", "VAR3": "3", "VAR4": "4"}
    result = replace_variables_recursive(settings, environ)

    assert result == {
        "prop": "1",
        "list": ["2"],
        "dict": {
            "var": "3",
            "subdict": {"var": "4"},
        },
    }
