import pytest


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

    # Read it back (no trailing slash for path parameters)
    response = client_with_db.get(f"/summaries/{summary_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == summary_id
    assert data["url"] == "https://foo.bar/"  # HttpUrl normalizes
    assert data["summary"] == ""  # Empty initially
    assert "created_at" in data


def test_read_summary_incorrect_id(client_with_db):
    """Test reading a summary with non-existent ID"""
    response = client_with_db.get("/summaries/999")
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


def test_read_summary_invalid_id(client_with_db):
    """Test reading a summary with invalid ID (id <= 0)."""
    response = client_with_db.get("/summaries/0")
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["type"] == "greater_than"
    assert detail[0]["loc"] == ["path", "summary_id"]


# ============================================================================
# DELETE Tests
# ============================================================================


def test_delete_summary(client_with_db):
    """Test deleting a summary."""
    # Create a summary
    response = client_with_db.post("/summaries/", json={"url": "https://foo.bar"})
    summary_id = response.json()["id"]

    # Delete it
    response = client_with_db.delete(f"/summaries/{summary_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == summary_id
    assert data["url"] == "https://foo.bar/"

    # Verify it's deleted
    response = client_with_db.get(f"/summaries/{summary_id}")
    assert response.status_code == 404


def test_delete_summary_not_found(client_with_db):
    """Test deleting a non-existent summary."""
    response = client_with_db.delete("/summaries/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_delete_summary_invalid_id(client_with_db):
    """Test deleting with invalid ID (id <= 0)."""
    response = client_with_db.delete("/summaries/0")
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["type"] == "greater_than"
    assert detail[0]["loc"] == ["path", "summary_id"]


# ============================================================================
# PUT Tests
# ============================================================================


def test_update_summary(client_with_db):
    """Test updating a summary."""
    # Create a summary
    response = client_with_db.post("/summaries/", json={"url": "https://foo.bar"})
    summary_id = response.json()["id"]

    # Update it
    update_payload = {"url": "https://updated.com", "summary": "updated content"}
    response = client_with_db.put(f"/summaries/{summary_id}", json=update_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == summary_id
    assert data["url"] == "https://updated.com/"  # HttpUrl normalizes
    assert data["summary"] == "updated content"
    assert "created_at" in data


def test_update_summary_not_found(client_with_db):
    """Test updating a non-existent summary."""
    update_payload = {"url": "https://foo.bar", "summary": "updated"}
    response = client_with_db.put("/summaries/999", json=update_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Summary not found"


def test_update_summary_invalid_id(client_with_db):
    """Test updating with invalid ID (id <= 0)."""
    update_payload = {"url": "https://foo.bar", "summary": "updated"}
    response = client_with_db.put("/summaries/0", json=update_payload)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["type"] == "greater_than"
    assert detail[0]["loc"] == ["path", "summary_id"]


def test_update_summary_invalid_url(client_with_db):
    """Test updating with invalid URL."""
    # Create a summary
    response = client_with_db.post("/summaries/", json={"url": "https://foo.bar"})
    summary_id = response.json()["id"]

    # Try to update with invalid URL
    update_payload = {"url": "invalid://url", "summary": "updated"}
    response = client_with_db.put(f"/summaries/{summary_id}", json=update_payload)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "url" in detail[0]["msg"].lower() or "url" in detail[0]["type"].lower()


def test_update_summary_missing_fields(client_with_db):
    """Test updating with missing required fields."""
    # Create a summary
    response = client_with_db.post("/summaries/", json={"url": "https://foo.bar"})
    summary_id = response.json()["id"]

    # Missing 'summary' field
    response = client_with_db.put(f"/summaries/{summary_id}", json={"url": "https://foo.bar"})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["type"] == "missing"
    assert detail[0]["loc"] == ["body", "summary"]

    # Missing 'url' field
    response = client_with_db.put(f"/summaries/{summary_id}", json={"summary": "updated"})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["type"] == "missing"
    assert detail[0]["loc"] == ["body", "url"]

    # Missing both fields
    response = client_with_db.put(f"/summaries/{summary_id}", json={})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert len(detail) == 2  # Two missing fields


# ============================================================================
# Parametrized Tests
# ============================================================================


@pytest.mark.parametrize(
    "summary_id,payload,expected_status,expected_detail_check",
    [
        # ID validation
        (
            0,
            {"url": "https://foo.bar", "summary": "test"},
            422,
            lambda d: d[0]["type"] == "greater_than",
        ),
        (
            -1,
            {"url": "https://foo.bar", "summary": "test"},
            422,
            lambda d: d[0]["type"] == "greater_than",
        ),
        # Not found
        (
            999,
            {"url": "https://foo.bar", "summary": "test"},
            404,
            lambda d: d == "Summary not found",
        ),
        # Invalid URL
        (1, {"url": "invalid://url", "summary": "test"}, 422, lambda d: "url" in str(d[0]).lower()),
        # Missing fields
        (1, {"url": "https://foo.bar"}, 422, lambda d: d[0]["type"] == "missing"),
        (1, {"summary": "test"}, 422, lambda d: d[0]["type"] == "missing"),
        (1, {}, 422, lambda d: len(d) == 2),
    ],
    ids=[
        "invalid_id_zero",
        "invalid_id_negative",
        "not_found",
        "invalid_url",
        "missing_summary",
        "missing_url",
        "missing_both",
    ],
)
def test_update_summary_validation_parametrized(
    client_with_db, summary_id, payload, expected_status, expected_detail_check
):
    """Parametrized test for PUT /summaries/{id} validation.

    This demonstrates modern pytest parametrization for testing
    multiple validation scenarios in a single test function.
    """
    # Create a summary if testing with id=1
    if summary_id == 1:
        response = client_with_db.post("/summaries/", json={"url": "https://foo.bar"})
        summary_id = response.json()["id"]

    response = client_with_db.put(f"/summaries/{summary_id}", json=payload)
    assert response.status_code == expected_status

    detail = response.json()["detail"]
    assert expected_detail_check(detail), f"Detail check failed for: {detail}"
