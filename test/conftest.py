import subprocess
import time

import httpx
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture()
def test_client():
    """FastAPI in-process test client (unit / API-logic tests)"""
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client


@pytest.fixture(scope="module")
def live_server():
    """
    Starts a real uvicorn process on port 18765 for physical download tests.
    Uses the same app code a browser talks to — real TCP, real cookie jar.
    """
    proc = subprocess.Popen(
        [
            "python", "-m", "uvicorn", "src.api.main:app",
            "--port", "18765", "--log-level", "error",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = "http://localhost:18765"
    # Poll /health until the server is ready (up to 5 seconds)
    for _ in range(20):
        try:
            httpx.get(f"{base}/health", timeout=0.5)
            break
        except Exception:
            time.sleep(0.25)
    yield base
    proc.terminate()
    proc.wait()
