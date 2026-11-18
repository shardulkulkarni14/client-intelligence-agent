import pytest

from client_intel import db


@pytest.fixture(scope="session")
def ds() -> db.Dataset:
    """The real starter pack, loaded once. Tests assert against known rows in it."""
    return db.load()
