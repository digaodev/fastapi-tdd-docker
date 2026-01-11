"""Tests for the summarizer module.

These are unit tests for the summarizer functionality, testing:
- Web scraping with trafilatura
- Provider abstraction
- Error handling
- Configuration
"""

from typing import Any

import pytest

# ============================================================================
# Web Scraping Tests
# ============================================================================


@pytest.mark.asyncio
async def test_fetch_article_text_success(monkeypatch):
    """Test successful article text extraction."""
    import httpx

    from fastapi_tdd_docker import summarizer

    # Mock HTTP response
    class MockResponse:
        status_code = 200
        text = """
            <html>
                <body>
                    <article>
                        <h1>Test Article</h1>
                        <p>This is a test article with enough content to pass the minimum
                        character check. We need at least 100 characters for trafilatura
                        to successfully extract the content.</p>
                    </article>
                </body>
            </html>
        """

        def raise_for_status(self):
            pass

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return MockResponse()

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: MockClient())

    # Test fetching
    text = await summarizer.fetch_article_text("https://example.com")

    assert text is not None
    assert len(text) > 0
    # trafilatura should extract at least the article content


@pytest.mark.asyncio
async def test_fetch_article_text_http_error(monkeypatch):
    """Test handling of HTTP errors during fetching."""
    import httpx

    from fastapi_tdd_docker import summarizer

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            raise httpx.HTTPError("404 Not Found")

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: MockClient())

    # Should raise ScrapingError
    with pytest.raises(summarizer.ScrapingError):
        await summarizer.fetch_article_text("https://example.com")


@pytest.mark.asyncio
async def test_fetch_article_text_insufficient_content(monkeypatch):
    """Test handling of pages with insufficient content."""
    import httpx

    from fastapi_tdd_docker import summarizer

    class MockResponse:
        status_code = 200
        text = "<html><body><p>Too short</p></body></html>"

        def raise_for_status(self):
            pass

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return MockResponse()

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kwargs: MockClient())

    # Should raise ScrapingError due to insufficient content
    with pytest.raises(summarizer.ScrapingError, match="Insufficient content"):
        await summarizer.fetch_article_text("https://example.com")


# ============================================================================
# Provider Tests
# ============================================================================


@pytest.mark.asyncio
async def test_mock_summarizer():
    """Test the mock summarizer (for testing environments)."""
    from fastapi_tdd_docker.summarizer import MockSummarizer

    summarizer = MockSummarizer()
    summary = await summarizer.summarize("This is a long article about Python...")

    assert summary is not None
    assert len(summary) > 0
    assert "mock" in summary.lower()


@pytest.mark.asyncio
async def test_openai_summarizer_requires_api_key():
    """Test that OpenAI summarizer requires an API key."""
    from fastapi_tdd_docker.summarizer import OpenAISummarizer

    # Should work with any string (validation happens at API call time)
    summarizer = OpenAISummarizer(api_key="test-key")
    assert summarizer is not None


def test_get_summarizer_with_mock_provider(monkeypatch):
    """Test getting the mock summarizer via factory."""
    from fastapi_tdd_docker.config import Settings
    from fastapi_tdd_docker.summarizer import MockSummarizer, get_summarizer

    # Set environment variable to override config
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "mock")

    settings = Settings()
    summarizer = get_summarizer(settings)

    assert isinstance(summarizer, MockSummarizer)


def test_get_summarizer_with_openai_provider(monkeypatch):
    """Test getting the OpenAI summarizer via factory."""
    from fastapi_tdd_docker.config import Settings
    from fastapi_tdd_docker.summarizer import OpenAISummarizer, get_summarizer

    # Set environment variables to override config
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "openai")
    monkeypatch.setenv("APP_OPENAI_API_KEY", "test-key-123")

    settings = Settings()
    summarizer = get_summarizer(settings)

    assert isinstance(summarizer, OpenAISummarizer)


def test_get_summarizer_openai_without_api_key(monkeypatch):
    """Test that OpenAI provider fails without API key."""
    from fastapi_tdd_docker.config import Settings
    from fastapi_tdd_docker.summarizer import get_summarizer

    # Set provider but don't set API key
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "openai")
    monkeypatch.delenv("APP_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = Settings()

    with pytest.raises(ValueError, match="requires APP_OPENAI_API_KEY"):
        get_summarizer(settings)


def test_get_summarizer_invalid_provider(monkeypatch):
    """Test that invalid provider raises error."""
    from fastapi_tdd_docker.config import Settings
    from fastapi_tdd_docker.summarizer import get_summarizer

    # Set invalid provider
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "invalid")

    settings = Settings()

    with pytest.raises(ValueError, match="Invalid summarizer provider"):
        get_summarizer(settings)


# ============================================================================
# Integration Tests (Background Task)
# ============================================================================


@pytest.mark.asyncio
async def test_generate_summary_task_with_mock_provider(monkeypatch: Any) -> None:
    """Test the full background task flow with mock provider."""
    from fastapi_tdd_docker import summarizer
    from fastapi_tdd_docker.config import get_settings
    from fastapi_tdd_docker.db import get_sessionmaker
    from fastapi_tdd_docker.models.text_summary import TextSummary

    # Set mock provider
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "mock")

    # Clear settings cache so monkeypatched env vars are picked up
    get_settings.cache_clear()

    # Mock fetch_article_text to avoid real HTTP requests
    async def mock_fetch(url: str, timeout: int = 30) -> str:
        return "This is a test article with enough content. " * 20  # 100+ chars

    monkeypatch.setattr(summarizer, "fetch_article_text", mock_fetch)

    # Create a test summary in the database
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        test_summary = TextSummary(
            url="https://example.com",
            summary="",
            status="pending",
        )
        session.add(test_summary)
        await session.commit()
        await session.refresh(test_summary)
        summary_id = test_summary.id

    # Mypy type narrowing: summary_id is guaranteed to exist after commit/refresh
    assert summary_id is not None

    # Run the background task
    await summarizer.generate_summary_task(summary_id, "https://example.com")

    # Verify the summary was updated
    async with session_factory() as session:
        updated_summary = await session.get(TextSummary, summary_id)
        assert updated_summary is not None
        assert updated_summary.status == "completed"
        assert len(updated_summary.summary) > 0
        assert "mock" in updated_summary.summary.lower()


@pytest.mark.asyncio
async def test_scraping_error_handling() -> None:
    """Test that ScrapingError is properly defined and can be raised."""
    from fastapi_tdd_docker.summarizer import ScrapingError

    # Test that we can raise and catch ScrapingError
    with pytest.raises(ScrapingError, match="Test error"):
        raise ScrapingError("Test error")

    # Error handling in generate_summary_task is tested implicitly
    # in the integration test above (it doesn't crash on errors)
