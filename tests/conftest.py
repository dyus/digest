from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def basic_feed() -> str:
    return (FIXTURES / "basic.xml").read_text()


@pytest.fixture
def empty_feed() -> str:
    return (FIXTURES / "empty.xml").read_text()
