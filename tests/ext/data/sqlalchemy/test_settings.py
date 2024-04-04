import pytest

from selva.ext.data.sqlalchemy.settings import SqlAlchemyEngineSettings


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
    ],
)
def test_sqlalchemy_settings_mutually_exclusive_properties(values: dict):
    with pytest.raises(ValueError):
        SqlAlchemyEngineSettings.model_validate({"url": "url"} | values)
