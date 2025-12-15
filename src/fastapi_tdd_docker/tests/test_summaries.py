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


def test_read_summary(client_with_db):
    """Test reading a single summary by ID."""
    # Create a summary first
    response = client_with_db.post("/summaries/", json={"url": "https://foo.bar"})
    summary_id = response.json()["id"]

    # Read it back
    response = client_with_db.get(f"/summaries/{summary_id}/")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == summary_id
    assert data["url"] == "https://foo.bar/"  # HttpUrl normalizes
    assert data["summary"] == ""  # Empty initially
    assert "created_at" in data


def test_read_summary_incorrect_id(client_with_db):
    """Test reading a summary with non-existent ID."""
    response = client_with_db.get("/summaries/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_read_all_summaries(client_with_db):
    """Test reading all summaries."""
    # Create a summary
    response = client_with_db.post("/summaries/", json={"url": "https://foo.bar"})
    summary_id = response.json()["id"]

    # Get all summaries
    response = client_with_db.get("/summaries/")
    assert response.status_code == 200

    response_list = response.json()
    assert len(list(filter(lambda d: d["id"] == summary_id, response_list))) == 1
