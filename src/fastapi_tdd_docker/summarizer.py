"""Modern text summarization service.

Supports multiple providers:
- OpenAI GPT-4o-mini (fast, cheap, high quality)
- Mock (for testing)

Can be extended to support:
- Local models (Hugging Face Transformers)
- Anthropic Claude
- Other LLM providers
"""

import logging
from abc import ABC, abstractmethod

import httpx
import trafilatura
from openai import AsyncOpenAI, OpenAIError

from fastapi_tdd_docker.config import Settings, get_settings
from fastapi_tdd_docker.db import get_sessionmaker
from fastapi_tdd_docker.models.text_summary import TextSummary

logger = logging.getLogger(__name__)


class SummarizationError(Exception):
    """Base exception for summarization errors."""

    pass


class ScrapingError(SummarizationError):
    """Raised when web scraping fails."""

    pass


class ProviderError(SummarizationError):
    """Raised when AI provider fails."""

    pass


# ============================================================================
# Web Scraping
# ============================================================================


async def fetch_article_text(url: str, timeout: int = 30) -> str:
    """Fetch and extract text content from a URL using trafilatura.

    Args:
        url: The URL to scrape
        timeout: Request timeout in seconds

    Returns:
        Extracted text content

    Raises:
        ScrapingError: If scraping fails
    """
    try:
        logger.info(f"Fetching article from: {url}")

        # Fetch HTML with timeout
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text

        # Extract text using trafilatura
        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            no_fallback=False,  # Try harder to extract content
        )

        if not text or len(text.strip()) < 100:
            raise ScrapingError(
                f"Insufficient content extracted from {url} (got {len(text or '')} chars)"
            )

        logger.info(f"Successfully extracted {len(text)} characters from {url}")
        return text

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e}")
        raise ScrapingError(f"Failed to fetch URL: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        raise ScrapingError(f"Failed to extract content: {e}") from e


# ============================================================================
# Summarization Providers
# ============================================================================


class SummarizerProvider(ABC):
    """Abstract base class for summarization providers."""

    @abstractmethod
    async def summarize(self, text: str, max_length: int = 300) -> str:
        """Generate a summary from text.

        Args:
            text: The text to summarize
            max_length: Maximum length of summary in words

        Returns:
            The generated summary
        """
        pass


class OpenAISummarizer(SummarizerProvider):
    """OpenAI-based summarizer using GPT-4o-mini."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def summarize(self, text: str, max_length: int = 300) -> str:
        """Generate a summary using OpenAI GPT-4o-mini.

        Args:
            text: The text to summarize
            max_length: Maximum length of summary in words

        Returns:
            The generated summary

        Raises:
            ProviderError: If OpenAI API call fails
        """
        try:
            # Truncate input if too long
            max_input_chars = 50000
            if len(text) > max_input_chars:
                logger.warning(f"Truncating input from {len(text)} to {max_input_chars} characters")
                text = text[:max_input_chars] + "..."

            logger.info(f"Calling OpenAI API to summarize {len(text)} characters")

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are a helpful assistant that creates concise, "
                            f"informative summaries of articles. Keep summaries under "
                            f"{max_length} words. Focus on the main points and key takeaways."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize this article:\n\n{text}",
                    },
                ],
                temperature=0.3,  # Lower temperature for more consistent summaries
                max_tokens=500,  # Enough for a good summary
            )

            summary = response.choices[0].message.content
            if not summary:
                raise ProviderError("OpenAI returned empty summary")

            logger.info(f"Successfully generated summary ({len(summary)} chars)")
            return summary.strip()

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ProviderError(f"OpenAI API failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI summarizer: {e}")
            raise ProviderError(f"Summarization failed: {e}") from e


class MockSummarizer(SummarizerProvider):
    """Mock summarizer for testing (doesn't call external APIs)."""

    async def summarize(self, text: str, max_length: int = 300) -> str:
        """Generate a mock summary (for testing).

        Args:
            text: The text to summarize (ignored)
            max_length: Maximum length (ignored)

        Returns:
            A mock summary
        """
        logger.info("Using mock summarizer (testing mode)")
        return (
            "This is a mock summary generated for testing purposes. "
            "In production, this would be a real AI-generated summary of the article content."
        )


# ============================================================================
# Provider Factory
# ============================================================================


def get_summarizer(settings: Settings | None = None) -> SummarizerProvider:
    """Get the configured summarizer provider.

    Args:
        settings: Application settings (uses default if None)

    Returns:
        Configured summarizer provider

    Raises:
        ValueError: If provider is invalid or required config is missing
    """
    if settings is None:
        settings = get_settings()

    provider = settings.summarizer_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OpenAI provider requires APP_OPENAI_API_KEY environment variable")
        logger.info("Using OpenAI summarizer (GPT-4o-mini)")
        return OpenAISummarizer(api_key=settings.openai_api_key)

    elif provider == "mock":
        logger.info("Using mock summarizer (testing mode)")
        return MockSummarizer()

    else:
        raise ValueError(f"Invalid summarizer provider: {provider}. Valid options: openai, mock")


# ============================================================================
# Background Task
# ============================================================================


async def generate_summary_task(summary_id: int, url: str) -> None:
    """Background task to generate and store a summary.

    This runs asynchronously after the API responds to the client.
    Updates the database with the generated summary or error status.

    Args:
        summary_id: The ID of the summary to update
        url: The URL to summarize
    """
    logger.info(f"Starting summarization task for summary_id={summary_id}, url={url}")

    session_factory = get_sessionmaker()
    async with session_factory() as session:
        try:
            # Update status to processing
            summary = await session.get(TextSummary, summary_id)
            if not summary:
                logger.error(f"Summary {summary_id} not found in database")
                return

            summary.status = "processing"
            await session.commit()

            # Fetch article text
            text = await fetch_article_text(url)

            # Generate summary
            summarizer = get_summarizer()
            summary_text = await summarizer.summarize(text)

            # Update database
            summary.summary = summary_text
            summary.status = "completed"
            await session.commit()

            logger.info(f"Successfully completed summarization for summary_id={summary_id}")

        except (ScrapingError, ProviderError) as e:
            # Handle expected errors
            logger.error(f"Summarization failed for summary_id={summary_id}: {e}")

            summary = await session.get(TextSummary, summary_id)
            if summary:
                summary.status = "failed"
                summary.summary = f"Failed to generate summary: {str(e)}"
                await session.commit()

        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"Unexpected error in summarization task for summary_id={summary_id}")

            try:
                summary = await session.get(TextSummary, summary_id)
                if summary:
                    summary.status = "failed"
                    summary.summary = f"Internal error: {str(e)}"
                    await session.commit()
            except Exception:
                logger.exception("Failed to update status to 'failed'")
