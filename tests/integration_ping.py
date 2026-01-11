"""Integration tests for /ping endpoint."""

import pytest


@pytest.mark.integration
def test_ping(client):
    """Integration test: Verify /ping endpoint returns correct response."""
    res = client.get("/ping")

    assert res.status_code == 200
    assert res.json() == {"ping": "pong!", "env": "dev", "test": True}
