import pytest


@pytest.fixture
def selenium(selenium):
    return selenium


def test_one(selenium):
    selenium.get("http://www.python.org")


def test_two(selenium):
    selenium.get("http://www.google.com")
