import os
from pathlib import Path

from selva._util import dotenv


def test_dotenv(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "dotenv")
    dotenv.init()

    assert "TEST_VARIABLE" in os.environ
    assert os.environ["TEST_VARIABLE"] == "value"


def test_dotenv_custom_location(monkeypatch):
    monkeypatch.setenv("SELVA_DOTENV", str(Path(__file__).parent / "dotenv" / ".env"))
    dotenv.init()

    assert "TEST_VARIABLE" in os.environ
    assert os.environ["TEST_VARIABLE"] == "value"
