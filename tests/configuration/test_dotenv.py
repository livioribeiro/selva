import os
from pathlib import Path


def test_dotenv(monkeypatch):
    monkeypatch.chdir(Path(__file__).parent / "dotenv")
    from selva import run

    assert "TEST_VARIABLE" in os.environ
    assert os.environ["TEST_VARIABLE"] == "value"


def test_dotenv_custom_location(monkeypatch):
    monkeypatch.setenv("SELVA_DOTENV", str(Path(__file__).parent / "dotenv" / ".env"))
    from selva import run

    assert "TEST_VARIABLE" in os.environ
    assert os.environ["TEST_VARIABLE"] == "value"
