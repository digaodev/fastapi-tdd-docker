"""CRUD operations for summaries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_tdd_docker.models.schemas import SummaryPayloadSchema, SummaryUpdateSchema
from fastapi_tdd_docker.models.text_summary import TextSummary


async def create_summary(session: AsyncSession, payload: SummaryPayloadSchema) -> TextSummary:
    """Create a new summary in the database."""
    summary = TextSummary(
        url=str(payload.url),
        summary="",  # Empty initially, will be populated by summarization service later
    )
    session.add(summary)
    await session.commit()
    await session.refresh(summary)
    return summary


async def get_summary(session: AsyncSession, summary_id: int) -> TextSummary | None:
    """Get a single summary by ID."""
    result = await session.execute(select(TextSummary).where(TextSummary.id == summary_id))
    return result.scalar_one_or_none()


async def get_all_summaries(session: AsyncSession) -> list[TextSummary]:
    """Get all summaries."""
    result = await session.execute(select(TextSummary))
    return list(result.scalars().all())


async def update_summary(
    session: AsyncSession, summary_id: int, payload: SummaryUpdateSchema
) -> TextSummary | None:
    """Update an existing summary."""
    summary = await get_summary(session, summary_id)
    if not summary:
        return None

    # Update fields
    summary.url = str(payload.url)
    summary.summary = payload.summary

    await session.commit()
    await session.refresh(summary)
    return summary


async def delete_summary(session: AsyncSession, summary_id: int) -> TextSummary | None:
    """Delete a summary by ID."""
    summary = await get_summary(session, summary_id)
    if not summary:
        return None

    await session.delete(summary)
    await session.commit()
    return summary
