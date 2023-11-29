import pytest
from streambridge.app import app


@pytest.fixture()
def app_client():
    yield app.test_client()
