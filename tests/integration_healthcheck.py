"""Integration tests for /health endpoint."""

import pytest


@pytest.mark.integration
def test_health_check_success(client_with_db):
    """Integration test: Health check with working database connection."""
    response = client_with_db.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["environment"] == "dev"


@pytest.mark.integration
def test_health_check_no_db(client):
    """Integration test: Health check without database (should fail gracefully)."""
    # This test uses 'client' fixture which has no DB dependency override
    # So it will try to connect to the actual database and may fail
    response = client.get("/health")

    # Could be 200 if DB is running, or 503 if not
    # Just verify it returns a valid response
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "database" in data
