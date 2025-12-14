def test_create_summary(client_with_db):
    """Test creating a new summary."""
    payload = {"url": "https://testdriven.io"}

    response = client_with_db.post("/summaries/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["url"] == "https://testdriven.io/"  # Pydantic HttpUrl normalizes URLs
    assert "id" in data
    assert isinstance(data["id"], int)


def test_create_summary_invalid_json(client_with_db):
    """Test creating summary with invalid payload."""
    response = client_with_db.post("/summaries/", json={})

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
