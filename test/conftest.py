
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture()
def test_client():
    """FastAPI test client"""
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client