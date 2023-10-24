from selva.configuration.environment import parse_settings, replace_variables


def test_parse_settings():
    source = {
        "SELVA__ENV1": "1",
        "SELVA__PATH1__ENV2": "2",
        "SELVA__PATH1__PATH2__SUB_ENV3": "3",
        "SELVA__": "None",
        "NOT_SELVA_ENV": "None",
    }

    result = parse_settings(source)

    expected = {
        "env1": "1",
        "path1": {
            "env2": "2",
            "path2": {
                "sub_env3": "3",
            },
        },
    }
    assert result == expected


def test_replace_variable_from_environ():
    yaml = "name: ${VAR}"
    result = replace_variables(yaml, {"VAR": "value"})

    assert result == "name: value"


def test_replace_variable_from_default():
    yaml = "name: ${VAR:default}"
    result = replace_variables(yaml, {})

    assert result == "name: default"


def test_replace_variable_environ_precedence():
    yaml = "name: ${VAR:default}"
    result = replace_variables(yaml, {"VAR": "value"})

    assert result == "name: value"
