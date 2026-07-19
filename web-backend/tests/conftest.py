import pytest
from fastapi.testclient import TestClient

from formfusion.config import Settings
from formfusion.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(
        environment="test",
        jwt_secret="test-secret-that-is-long-enough-for-tests",
        allowed_origins=["http://testserver"],
        frame_queue_capacity=4,
        frame_sync_tolerance_ms=60,
    )


@pytest.fixture
def client(settings: Settings):
    with TestClient(create_app(settings)) as test_client:
        yield test_client
