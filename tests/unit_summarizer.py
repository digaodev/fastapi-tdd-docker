"""Unit tests for the summarizer module.

These are pure unit tests with all external dependencies mocked:
- Web scraping with trafilatura (HTTP mocked)
- Provider abstraction (no external API calls)
- Error handling
- Configuration
"""

from typing import Any

import pytest

# ============================================================================
# Web Scraping Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_article_text_success(monkeypatch):
    """Unit test: Mock HTTP response and test text extraction logic."""
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_article_text_http_error(monkeypatch):
    """Unit test: Verify HTTP error handling."""
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_article_text_insufficient_content(monkeypatch):
    """Unit test: Verify handling of pages with too little content."""
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


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mock_summarizer():
    """Unit test: Verify mock summarizer returns expected format."""
    from fastapi_tdd_docker.summarizer import MockSummarizer

    summarizer = MockSummarizer()
    summary = await summarizer.summarize("This is a long article about Python...")

    assert summary is not None
    assert len(summary) > 0
    assert "mock" in summary.lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openai_summarizer_requires_api_key():
    """Unit test: Verify OpenAI summarizer can be instantiated with API key."""
    from fastapi_tdd_docker.summarizer import OpenAISummarizer

    # Should work with any string (validation happens at API call time)
    summarizer = OpenAISummarizer(api_key="test-key")
    assert summarizer is not None


@pytest.mark.unit
def test_get_summarizer_with_mock_provider(monkeypatch):
    """Unit test: Verify factory returns mock provider."""
    from fastapi_tdd_docker.config import Settings
    from fastapi_tdd_docker.summarizer import MockSummarizer, get_summarizer

    # Set environment variable to override config
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "mock")

    settings = Settings()
    summarizer = get_summarizer(settings)

    assert isinstance(summarizer, MockSummarizer)


@pytest.mark.unit
def test_get_summarizer_with_openai_provider(monkeypatch):
    """Unit test: Verify factory returns OpenAI provider."""
    from fastapi_tdd_docker.config import Settings
    from fastapi_tdd_docker.summarizer import OpenAISummarizer, get_summarizer

    # Set environment variables to override config
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "openai")
    monkeypatch.setenv("APP_OPENAI_API_KEY", "test-key-123")

    settings = Settings()
    summarizer = get_summarizer(settings)

    assert isinstance(summarizer, OpenAISummarizer)


@pytest.mark.unit
def test_get_summarizer_openai_without_api_key(monkeypatch):
    """Unit test: Verify OpenAI provider fails without API key."""
    from fastapi_tdd_docker.config import Settings
    from fastapi_tdd_docker.summarizer import get_summarizer

    # Set provider but don't set API key
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "openai")
    monkeypatch.delenv("APP_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    settings = Settings()

    with pytest.raises(ValueError, match="requires APP_OPENAI_API_KEY"):
        get_summarizer(settings)


@pytest.mark.unit
def test_get_summarizer_invalid_provider(monkeypatch):
    """Unit test: Verify factory rejects invalid provider."""
    from fastapi_tdd_docker.config import Settings
    from fastapi_tdd_docker.summarizer import get_summarizer

    # Set invalid provider
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "invalid")

    settings = Settings()

    with pytest.raises(ValueError, match="Invalid summarizer provider"):
        get_summarizer(settings)


# ============================================================================
# Background Task Tests (with all dependencies mocked)
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_summary_task_can_be_called(monkeypatch: Any) -> None:
    """Unit test: Verify background task can execute without crashing.

    This is a pure unit test that mocks all database and external dependencies.
    Full integration testing of the background task is in integration_summaries.py.
    """
    from fastapi_tdd_docker import summarizer

    # Set mock provider
    monkeypatch.setenv("APP_SUMMARIZER_PROVIDER", "mock")

    # Track if the summarization was attempted
    summarization_called = False

    # Mock get_sessionmaker to return a mock session factory
    class MockSummary:
        def __init__(self) -> None:
            self.id = 1
            self.url = "https://example.com"
            self.summary = ""
            self.status = "pending"

    class MockSession:
        async def get(self, model: Any, id: int) -> MockSummary:
            return MockSummary()

        async def commit(self) -> None:
            pass

        async def __aenter__(self) -> "MockSession":
            return self

        async def __aexit__(self, *args: Any) -> None:
            pass

    class MockSessionFactory:
        def __call__(self):
            return MockSession()

    # Mock fetch_article_text to return content
    async def mock_fetch(url: str, timeout: int = 30) -> str:
        return "This is a test article with enough content. " * 20

    # Mock get_summarizer to track calls
    def mock_get_summarizer(settings=None):
        nonlocal summarization_called
        summarization_called = True
        return summarizer.MockSummarizer()

    # Apply mocks
    monkeypatch.setattr(summarizer, "fetch_article_text", mock_fetch)
    monkeypatch.setattr(summarizer, "get_summarizer", mock_get_summarizer)
    mock_session_factory = MockSessionFactory()
    monkeypatch.setattr(summarizer, "get_sessionmaker", lambda: mock_session_factory)

    # Run the background task (should not raise)
    await summarizer.generate_summary_task(1, "https://example.com")

    # Verify the summarizer was invoked
    assert summarization_called, "Summarizer should have been called"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_scraping_error_handling() -> None:
    """Unit test: Verify ScrapingError exception can be raised and caught."""
    from fastapi_tdd_docker.summarizer import ScrapingError

    # Test that we can raise and catch ScrapingError
    with pytest.raises(ScrapingError, match="Test error"):
        raise ScrapingError("Test error")

    # Error handling in generate_summary_task is tested implicitly
    # in the integration test (it doesn't crash on errors)
