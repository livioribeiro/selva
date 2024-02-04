import pytest

from selva.data.sqlalchemy.settings import SqlAlchemySettings, SqlAlchemyOptions


@pytest.mark.parametrize(
    "values",
    [
        {"host": "host"},
        {"port": 5432},
        {"database": "database"},
        {"host": "host", "port": 5423},
        {"host": "host", "port": 5432, "database": "database"},
    ],
    ids=[
        "host",
        "port",
        "database",
        "host_port",
        "host_port_database",
    ]
)
def test_sqlalchemy_settings_mutually_exclusive_properties(values: dict):
    with pytest.raises(ValueError):
        SqlAlchemySettings.model_validate({"url": "url"} | values)
