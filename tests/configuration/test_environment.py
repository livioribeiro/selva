import pytest

from selva.configuration import environment as env


def test_get_str(monkeypatch):
    monkeypatch.setenv("VALUE", "str")
    result = env.get_str("VALUE")
    assert result == "str"


def test_undefined_environment_variable_should_fail():
    with pytest.raises(KeyError, match=f"Environment variable 'DOES_NOT_EXIST' is not defined"):
        env.get_str("DOES_NOT_EXIST")


def test_get_int(monkeypatch):
    monkeypatch.setenv("VALUE", "123")
    result = env.get_int("VALUE")
    assert result == 123


def test_get_int_with_invalid_value_should_fail(monkeypatch):
    monkeypatch.setenv("VALUE", "abc")
    with pytest.raises(ValueError):
        env.get_int("VALUE")


def test_get_float(monkeypatch):
    monkeypatch.setenv("VALUE", "1.23")
    result = env.get_float("VALUE")
    assert result == 1.23


def test_get_float_with_invalid_should_fail(monkeypatch):
    monkeypatch.setenv("VALUE", "abc")
    with pytest.raises(ValueError):
        env.get_float("VALUE")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("true", True),
        ("True", True),
        ("1", True),
        ("false", False),
        ("False", False),
        ("0", False),
    ],
    ids=["true", "True", "1", "false", "False", "0"]
)
def test_get_bool(raw, expected, monkeypatch):
    monkeypatch.setenv("VALUE", raw)
    result = env.get_bool("VALUE")
    assert result == expected


def test_get_bool_with_invalid_should_fail(monkeypatch):
    monkeypatch.setenv("VALUE", "abc")
    with pytest.raises(ValueError):
        env.get_bool("VALUE")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("abc", ["abc"]),
        ("abc,", ["abc", ""]),
        ("abc,,", ["abc", "", ""]),
        (",abc", ["", "abc"]),
        (",,abc", ["", "", "abc"]),
        ("abc,def,ghi", ["abc", "def", "ghi"]),
        ('"abc","def","ghi"', ["abc", "def", "ghi"]),
        ("'abc','def','ghi'", ["abc", "def", "ghi"]),
        ('"abc",def,ghi', ["abc", "def", "ghi"]),
        ("'abc',def,ghi", ["abc", "def", "ghi"]),
        (" abc,def , ghi ", ["abc", "def", "ghi"]),
        ("'abc ',' def',' ghi '", ["abc ", " def", " ghi "]),
        (" 'abc ',' def', ' ghi ' ", ["abc ", " def", " ghi "]),
    ],
    ids=[
        "abc",
        "abc,",
        "abc,,",
        ",abc",
        ",,abc",
        "abc,def,ghi",
        '"abc","def","ghi"',
        "'abc','def','ghi'",
        '"abc",def,ghi',
        "'abc',def,ghi",
        " abc,def , ghi ",
        "'abc ',' def',' ghi '",
        " 'abc ',' def', ' ghi ' ",
    ]
)
def test_get_list(raw, expected, monkeypatch):
    monkeypatch.setenv("VALUE", raw)
    result = env.get_list("VALUE")
    assert result == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("a=1", {"a": "1"}),
        ("a=1,b=2", {"a": "1", "b": "2"}),
        ("'a'=1,b='2','c'='3'", {"a": "1", "b": "2", "c": "3"}),
        ('"a"=1,b="2","c"="3"', {"a": "1", "b": "2", "c": "3"}),
        ("'a'=\"1\",\"b\"='2','c'='3',\"d\"=\"4\"", {"a": "1", "b": "2", "c": "3", "d": "4"}),
        ("a =1 , b= 2, c = 3 ", {"a": "1", "b": "2", "c": "3"}),
        ("'a '='1 ',' b'=' 2',' c '=' 3 '", {"a ": "1 ", " b": " 2", " c ": " 3 "}),
    ],
    ids=[
        "a=1",
        "a=1,b=2",
        "'a'=1,b='2','c'='3'",
        '"a"=1,b="2","c"="3"',
        "'a'=\"1\",\"b\"='2','c'='3',\"d\"=\"4\"",
        "a =1 , b= 2, c = 3 ",
        "'a '='1 ',' b'=' 2',' c '=' 3 '",
    ]
)
def test_get_dict(raw, expected, monkeypatch):
    monkeypatch.setenv("VALUE", raw)
    result = env.get_dict("VALUE")
    assert result == expected


@pytest.mark.parametrize(
    "value",
    [
        "a",
        "a=",
        "a=1,",
        ",a=1"
    ]
)
def test_get_dict_with_invalid_should_fail(value, monkeypatch):
    monkeypatch.setenv("VALUE", value)
    with pytest.raises(ValueError):
        env.get_bool("VALUE")


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1", 1),
        ("1.2", 1.2),
        ("true", True),
        ("false", False),
        ("null", None),
        ('"1"', "1"),
        ('"1.2"', "1.2"),
        ('"true"', "true"),
        ('"false"', "false"),
        ('"null"', "null"),
        ("[1, 2, 3]", [1, 2, 3]),
        ('["a", "b", "c"]', ["a", "b", "c"]),
        ('{"a": 1, "b": 1.2, "c": "3", "d": true, "e": null}', {"a": 1, "b": 1.2, "c": "3", "d": True, "e": None})
    ],
    ids=[
        "1",
        "1.2",
        "true",
        "false",
        "null",
        '"1"',
        '"1.2"',
        '"true"',
        '"false"',
        '"null"',
        "[1, 2, 3]",
        '["a", "b", "c"]',
        '{"a": 1, "b": 1.2, "c": "3", "d": true, "e": null}',
    ]
)
def test_get_json(raw, expected, monkeypatch):
    monkeypatch.setenv("VALUE", raw)
    result = env.get_json("VALUE")
    assert result == expected


def test_get_json_with_invalid_should_fail(monkeypatch):
    monkeypatch.setenv("VALUE", "abc")
    with pytest.raises(ValueError):
        env.get_bool("VALUE")
