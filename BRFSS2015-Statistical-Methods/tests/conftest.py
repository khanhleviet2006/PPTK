import pytest
from src.data.synthetic import generate


@pytest.fixture
def synthetic():
    return generate(960)
